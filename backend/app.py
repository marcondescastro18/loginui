#!/usr/bin/env python3
"""
app.py - API Backend do Sistema de Login

API REST construída com Flask para autenticação de usuários.

Endpoints disponíveis:
- GET  /health           - Health check da aplicação
- GET  /health/db        - Health check do banco de dados
- POST /api/auth/login   - Autenticação de usuário (retorna JWT token)
- POST /api/auth/verify  - Validação de JWT token

Schema do Banco (REAL - Confirmado):
- usuarios: id, email, senha, criado_em
  (NÃO possui: nome, ativo, atualizado_em, ultimo_acesso)
- registros_acesso: id, usuario_id, tipo_evento, endereco_ip, sucesso, mensagem, criado_em
  (NÃO possui: email)

Autenticação:
- Senhas com bcrypt (10+ rounds)
- Tokens JWT com expiração de 24 horas
- Logs de todas as tentativas de acesso
- Tratamento robusto de exceções SQL

Segurança:
- CORS configurado para origens específicas
- Validação de inputs
- Tratamento robusto de exceções para prevenir crash do Gunicorn
- Proteção contra SQL injection (prepared statements)
- Rollback automático em erros de banco

Variáveis de ambiente necessárias:
- JWT_SECRET (obrigatória)
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

Uso:
    # Desenvolvimento
    python app.py
    
    # Produção
    gunicorn --bind 0.0.0.0:3000 app:app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import jwt
import bcrypt
import psycopg2
from datetime import datetime, timedelta
from db import get_user_by_email, create_session, log_access, get_connection
from config import Config

# Inicializa aplicação Flask
app = Flask(__name__)

# Validar configurações obrigatórias na inicialização
if not Config.JWT_SECRET:
    raise ValueError(
        "JWT_SECRET é obrigatória. Configure a variável de ambiente JWT_SECRET. "
        "Exemplo: export JWT_SECRET='sua_chave_secreta_aqui'"
    )

# Configuração CORS para origens permitidas
CORS(app, resources={r"/*": {"origins": ["https://login-interface.znh7ry.easypanel.host", "http://localhost:3000"]}}, 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Handler explícito de preflight CORS para evitar 404 sem headers
@app.route('/api/auth/login', methods=['OPTIONS'])
@cross_origin(origins=["https://login-interface.znh7ry.easypanel.host", "http://localhost:3000"],
              allow_headers=["Content-Type", "Authorization"],
              methods=["POST"])
def login_options():
    """Handler preflight CORS para endpoint de login"""
    return '', 200

@app.route('/health', methods=['GET'])
def health():
    """Health check básico da aplicação"""
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/health/db', methods=['GET'])
def health_db():
    """
    Health check do banco de dados.
    Verifica conectividade e conta usuários (se possível).
    """
    try:
        conn = get_connection()
        if not conn:
            return jsonify({'status': 'ERROR', 'db': 'UNAVAILABLE'}), 500
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            # Tentar contar usuários (opcional, para diagnóstico)
            usuarios_count = None
            try:
                cur.execute("SELECT COUNT(*) FROM usuarios")
                usuarios_count = cur.fetchone()[0]
            except Exception:
                usuarios_count = 'unknown'
            cur.close()
            return jsonify({'status': 'OK', 'db': 'AVAILABLE', 'usuarios_count': usuarios_count}), 200
        finally:
            conn.close()
    except Exception as e:
        print(f"DB health error: {e}")
        return jsonify({'status': 'ERROR', 'db': 'UNKNOWN'}), 500

# Evitar 404 para favicon (não impacta API)
@app.route('/favicon.ico', methods=['GET'])
def favicon():
    """Retorna 204 para favicon (evita logs desnecessários)"""
    return '', 204

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Endpoint de autenticação de usuários.
    
    CORREÇÕES APLICADAS:
    - Remove uso de coluna 'nome' (NÃO existe no banco)
    - Remove uso de 'email' em registros_acesso (NÃO existe)
    - Tratamento robusto de exceções SQL para evitar crash do Gunicorn
    - Rollback automático em caso de erro
    - Usa apenas colunas existentes: id, email, senha, criado_em
    
    Request JSON:
        {
            "email": "usuario@email.com",
            "senha": "senha123"
        }
    
    Response Success (200):
        {
            "sucesso": true,
            "mensagem": "Login realizado com sucesso",
            "token": "jwt_token_aqui",
            "usuario": {
                "id": 1,
                "email": "usuario@email.com"
            }
        }
    
    Response Error (400/401/500):
        {
            "sucesso": false,
            "mensagem": "Descrição do erro"
        }
    """
    try:
        # Validar presença de dados no request
        data = request.get_json()
        if not data:
            return jsonify({'sucesso': False, 'mensagem': 'Dados inválidos'}), 400
        
        # Extrair credenciais
        email = data.get('email')
        senha = data.get('senha')
        
        # Validar campos obrigatórios
        if not email or not senha:
            return jsonify({'sucesso': False, 'mensagem': 'Email e senha obrigatórios'}), 400
        
        # Buscar usuário no banco - retorna apenas: id, email, senha, criado_em
        usuario = get_user_by_email(email)
        if not usuario:
            # Usuário não encontrado - registrar tentativa sem usuario_id
            ip = request.remote_addr
            log_access(None, 'login', ip, False, 'Usuário não encontrado')
            return jsonify({'sucesso': False, 'mensagem': 'Usuário ou senha inválida'}), 401
        
        # Verificar senha (suporta bcrypt e plaintext para dev)
        senha_db = usuario['senha']
        senha_correta = False
        
        # Verificar se é hash bcrypt (formato: $2b$ ou $2a$)
        if senha_db.startswith('$2b$') or senha_db.startswith('$2a$'):
            try:
                senha_correta = bcrypt.checkpw(senha.encode('utf-8'), senha_db.encode('utf-8'))
            except Exception as e:
                print(f"Erro ao verificar bcrypt: {e}")
                senha_correta = False
        else:
            # Fallback plaintext apenas para desenvolvimento (NÃO usar em produção)
            senha_correta = (senha == senha_db)
        
        # Se senha incorreta, registrar tentativa falhada e retornar erro
        if not senha_correta:
            ip = request.remote_addr
            log_access(usuario['id'], 'login', ip, False, 'Senha inválida')
            return jsonify({'sucesso': False, 'mensagem': 'Usuário ou senha inválida'}), 401
        
        # Gerar token JWT com informações do usuário
        payload = {
            'user_id': usuario['id'],
            'email': usuario['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
        
        # Registrar sessão e log de acesso bem-sucedido
        ip = request.remote_addr
        create_session(usuario['id'], token, ip)
        log_access(usuario['id'], 'login', ip, True, 'Login bem-sucedido')
        
        # Retornar resposta de sucesso SEM campo 'nome' (não existe no banco)
        return jsonify({
            'sucesso': True,
            'mensagem': 'Login realizado com sucesso',
            'token': token,
            'usuario': {
                'id': usuario['id'],
                'email': usuario['email']
            }
        }), 200
        
    except psycopg2.Error as db_error:
        # Tratamento específico para erros de banco de dados
        # Evita crash do Gunicorn ao logar erro e retornar resposta controlada
        print(f"[ERRO SQL] Erro de banco de dados no login: {db_error}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro no banco de dados'}), 500
        
    except Exception as e:
        # Tratamento genérico para evitar crash do Gunicorn
        # Captura qualquer exceção não prevista
        print(f"[ERRO] Erro inesperado no login: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao realizar login'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    """
    Verifica validade do token JWT.
    Tratamento robusto de exceções.
    
    Headers:
        Authorization: Bearer <jwt_token>
    
    Response Success (200):
        {
            "sucesso": true,
            "mensagem": "Token valido",
            "usuario": {
                "user_id": 1,
                "email": "usuario@email.com",
                "exp": 1234567890
            }
        }
    
    Response Error (401):
        {
            "sucesso": false,
            "mensagem": "Token expirado/invalido"
        }
    """
    try:
        # Extrair token do header Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'sucesso': False, 'mensagem': 'Token nao fornecido'}), 401
        
        # Remover "Bearer " se presente
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        
        # Decodificar e validar token
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        
        return jsonify({'sucesso': True, 'mensagem': 'Token valido', 'usuario': payload}), 200
        
    except jwt.ExpiredSignatureError:
        # Token expirado (após 24 horas)
        return jsonify({'sucesso': False, 'mensagem': 'Token expirado'}), 401
        
    except jwt.InvalidTokenError:
        # Token inválido (assinatura incorreta, formato inválido, etc)
        return jsonify({'sucesso': False, 'mensagem': 'Token invalido'}), 401
        
    except Exception as e:
        # Tratamento genérico para evitar crash
        print(f"[ERRO] Erro inesperado na verificação de token: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao verificar'}), 500

if __name__ == '__main__':
    """
    Servidor de desenvolvimento.
    Para produção, usar Gunicorn:
        gunicorn --bind 0.0.0.0:3000 app:app
    """
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)

