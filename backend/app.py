from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import jwt
import bcrypt
import psycopg2
from datetime import datetime, timedelta
from db import get_user_by_email, create_session, log_access, update_last_access, get_connection
from config import Config

app = Flask(__name__)

# Validar configurações obrigatórias
if not Config.JWT_SECRET:
    raise ValueError("JWT_SECRET é obrigatória. Configure a variável de ambiente JWT_SECRET.")
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
    return '', 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/health/db', methods=['GET'])
def health_db():
    try:
        conn = get_connection()
        if not conn:
            return jsonify({'status': 'ERROR', 'db': 'UNAVAILABLE'}), 500
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            # tentar checar tabela usuarios (opcional)
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
    return '', 204

@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    Endpoint de autenticação.
    Totalmente compatível com schema sem coluna 'nome' e sem 'email' em registros_acesso.
    Tratamento robusto de exceções para evitar crash do Gunicorn.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'sucesso': False, 'mensagem': 'Dados inválidos'}), 400
        
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'sucesso': False, 'mensagem': 'Email e senha obrigatórios'}), 400
        
        # Buscar usuário - retorna apenas id, email, senha
        usuario = get_user_by_email(email)
        if not usuario:
            ip = request.remote_addr
            # log_access agora sem parâmetro 'email'
            log_access(None, 'login', ip, False, 'Usuário não encontrado')
            return jsonify({'sucesso': False, 'mensagem': 'Usuário ou senha inválida'}), 401
        
        # Verificar senha (bcrypt ou plaintext para dev)
        senha_db = usuario['senha']
        senha_correta = False
        
        if senha_db.startswith('$2b$') or senha_db.startswith('$2a$'):
            try:
                senha_correta = bcrypt.checkpw(senha.encode('utf-8'), senha_db.encode('utf-8'))
            except Exception as e:
                print(f"Erro ao verificar bcrypt: {e}")
                senha_correta = False
        else:
            # Fallback plaintext apenas para desenvolvimento
            senha_correta = (senha == senha_db)
        
        if not senha_correta:
            ip = request.remote_addr
            log_access(None, 'login', ip, False, 'Senha inválida')
            return jsonify({'sucesso': False, 'mensagem': 'Usuário ou senha inválida'}), 401
        
        # Gerar token JWT
        payload = {
            'user_id': usuario['id'],
            'email': usuario['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
        
        # Registrar sessão e logs
        ip = request.remote_addr
        create_session(usuario['id'], token, ip)
        log_access(usuario['id'], 'login', ip, True, 'Login bem-sucedido')
        update_last_access(usuario['id'])
        
        # Resposta JSON sem campo 'nome' (não existe no banco)
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
        # Tratamento específico para erros de banco
        print(f"Erro de banco de dados no login: {db_error}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro no banco de dados'}), 500
    except Exception as e:
        # Tratamento genérico para evitar crash do Gunicorn
        print(f"Erro inesperado no login: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao realizar login'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    """
    Verifica validade do token JWT.
    Tratamento robusto de exceções.
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'sucesso': False, 'mensagem': 'Token nao fornecido'}), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return jsonify({'sucesso': True, 'mensagem': 'Token valido', 'usuario': payload}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'sucesso': False, 'mensagem': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'sucesso': False, 'mensagem': 'Token invalido'}), 401
    except Exception as e:
        print(f"Erro inesperado na verificação de token: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao verificar'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
