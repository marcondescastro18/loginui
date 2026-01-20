from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import jwt
import bcrypt
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

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'sucesso': False, 'mensagem': 'Email e senha obrigatorios'}), 400
        
        usuario = get_user_by_email(email)
        if not usuario:
            ip = request.remote_addr
            log_access(None, email, 'login', ip, False, 'Usuario nao encontrado')
            return jsonify({'sucesso': False, 'mensagem': 'Usuario ou senha invalida'}), 401
        
        # Verificar se a senha está em bcrypt ou plaintext
        senha_db = usuario['senha']
        if senha_db.startswith('$2b$') or senha_db.startswith('$2a$'):
            # Senha hasheada com bcrypt
            senha_correta = bcrypt.checkpw(senha.encode(), senha_db.encode())
        else:
            # Senha em plaintext
            senha_correta = (senha == senha_db)
        
        if not senha_correta:
            ip = request.remote_addr
            log_access(None, email, 'login', ip, False, 'Senha invalida')
            return jsonify({'sucesso': False, 'mensagem': 'Usuario ou senha invalida'}), 401
        
        payload = {'id': usuario['id'], 'email': usuario['email'], 'exp': datetime.utcnow() + timedelta(hours=24)}
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
        
        ip = request.remote_addr
        create_session(usuario['id'], token, ip)
        log_access(usuario['id'], email, 'login', ip, True, 'Login bem-sucedido')
        update_last_access(usuario['id'])
        
        nome = usuario.get('nome') or usuario['email']
        return jsonify({'sucesso': True, 'mensagem': 'Login realizado', 'token': token, 'usuario': {'id': usuario['id'], 'email': usuario['email'], 'nome': nome}}), 200
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao realizar login'}), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
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
        print(f"Erro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao verificar'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
