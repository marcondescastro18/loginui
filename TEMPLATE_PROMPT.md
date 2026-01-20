# 📋 Modelo de Prompt - React + Python Flask + PostgreSQL

## Descrição do Projeto
Sistema completo de autenticação com:
- **Frontend:** Vite + React + TypeScript + Axios
- **Backend:** Python Flask + JWT + bcrypt
- **Banco:** PostgreSQL
- **Deploy:** EasyPanel com Nixpacks

---

## 📁 Estrutura do Projeto

```
projeto/
├── src/                          # Frontend React
│   ├── pages/
│   │   ├── Login.tsx            # Página de login
│   │   └── Success.tsx          # Página de sucesso
│   ├── services/
│   │   └── api.ts               # Cliente Axios configurado
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   └── App.css
├── backend/                      # Backend Python
│   ├── app.py                   # Aplicação Flask
│   ├── config.py                # Configuração (variáveis env)
│   ├── db.py                    # Funções de banco de dados
│   ├── requirements.txt         # Dependências Python
│   ├── Procfile                 # Comando de inicialização (gunicorn)
│   └── runtime.txt              # Versão do Python
├── banco_dados/
│   ├── schema.sql               # Schema do PostgreSQL
│   └── db-config.js             # Configuração de conexão (local)
├── public/                       # Arquivos estáticos
├── vite.config.ts               # Configuração Vite (allowedHosts)
├── package.json                 # Dependências Node
├── tsconfig.json
├── index.html
└── README.md
```

---

## 🛠️ Configurações de Arquivo

### 1. **package.json** (Frontend)
```json
{
  "name": "seu-projeto",
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "vite preview --host 0.0.0.0 --port 3000 --strictPort",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.13.2",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-router-dom": "^7.12.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.1.1",
    "typescript": "~5.9.3",
    "vite": "^7.2.4"
  }
}
```

### 2. **vite.config.ts** (Frontend - allowedHosts)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    sourcemap: false,
  },
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    allowedHosts: ['seu-dominio-publico.easypanel.host'],
  },
})
```

### 3. **src/services/api.ts** (Configuração Axios)
```typescript
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "https://seu-backend.easypanel.host";

export const api = axios.create({
  baseURL: API_URL,
});
```

### 4. **backend/requirements.txt** (Python)
```
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
PyJWT==2.10.1
bcrypt==4.1.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

### 5. **backend/Procfile** (Deploy gunicorn)
```
web: gunicorn -b 0.0.0.0:${PORT:-3000} app:app
```

### 6. **backend/runtime.txt** (Versão Python)
```
python-3.11.7
```

### 7. **backend/config.py** (Configuração com env vars)
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'postgres')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'auth_db')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Senha123456')
    DB_NAME = os.getenv('DB_NAME', 'auth_db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'sua_chave_secreta_aqui')
    DEBUG = os.getenv('DEBUG', False)
    PORT = int(os.getenv('PORT', 3000))
```

### 8. **backend/db.py** (Funções de Banco)
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return None

def get_user_by_email(email):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, email, senha, nome FROM usuarios WHERE email = %s AND ativo = TRUE", (email,))
        user = cur.fetchone()
        cur.close()
        return user
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def create_session(usuario_id, token, ip_address):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')", (usuario_id, token, ip_address))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()

def log_access(usuario_id, email, tipo_evento, ip_address, sucesso, mensagem):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO registros_acesso (usuario_id, email, tipo_evento, endereco_ip, sucesso, mensagem) VALUES (%s, %s, %s, %s, %s, %s)", (usuario_id, email, tipo_evento, ip_address, sucesso, mensagem))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()

def update_last_access(usuario_id):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = %s", (usuario_id,))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()
```

### 9. **backend/app.py** (Flask com rotas)
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta
from db import get_user_by_email, create_session, log_access, update_last_access
from config import Config

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK', 'timestamp': datetime.now().isoformat()}), 200

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
        
        senha_correta = bcrypt.checkpw(senha.encode(), usuario['senha'].encode())
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
        
        return jsonify({'sucesso': True, 'mensagem': 'Login realizado', 'token': token, 'usuario': {'id': usuario['id'], 'email': usuario['email'], 'nome': usuario['nome']}}), 200
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
```

### 10. **banco_dados/schema.sql** (PostgreSQL)
```sql
CREATE TABLE IF NOT EXISTS usuarios (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  nome VARCHAR(255),
  ativo BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  ultimo_acesso TIMESTAMP NULL,
  CONSTRAINT email_not_empty CHECK (email != '')
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios(ativo);

CREATE TABLE IF NOT EXISTS sessoes (
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  endereco_ip VARCHAR(50),
  agente_usuario VARCHAR(255),
  expirado_em TIMESTAMP NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT token_not_empty CHECK (token != '')
);

CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token);
CREATE INDEX IF NOT EXISTS idx_sessoes_usuario_id ON sessoes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_expirado_em ON sessoes(expirado_em);

CREATE TABLE IF NOT EXISTS registros_acesso (
  id SERIAL PRIMARY KEY,
  usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
  email VARCHAR(255),
  tipo_evento VARCHAR(50),
  endereco_ip VARCHAR(50),
  sucesso BOOLEAN,
  mensagem VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_registros_usuario_id ON registros_acesso(usuario_id);
CREATE INDEX IF NOT EXISTS idx_registros_criado_em ON registros_acesso(criado_em);

-- Usuário de teste (senha: 123456)
INSERT INTO usuarios (email, nome, senha) VALUES 
('teste@email.com', 'Usuário Teste', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIIHXWqasi');
```

---

## 🚀 Deploy no EasyPanel

### **PASSO 1: PostgreSQL Database**
1. Crie um serviço PostgreSQL:
   - Nome: `postgres`
   - Database: `auth_db`
   - Username: `auth_db`
   - Password: `Senha123456`

2. Execute o schema.sql no console do banco

### **PASSO 2: Backend (Flask)**
1. Crie um serviço App:
   - Nome: `login-api`
   - Source: GitHub
   - Repository: `seu-usuario/seu-repo`
   - Branch: `main`
   - Build: Nixpacks
   - Build Path: `backend`

2. Environment Variables:
   ```
   DB_HOST=postgres
   DB_PORT=5432
   DB_USER=auth_db
   DB_PASSWORD=Senha123456
   DB_NAME=auth_db
   JWT_SECRET=sk-prod-2026-login-system-az9x4kL8pQ2mN6tV1wJe3rF5uD7sB9cH0
   PORT=3000
   ```

3. Domínios:
   - HTTPS: Ativado
   - Destino Protocolo: HTTP
   - Destino Porta: 3000
   - Caminho: /

4. Implante e teste: `https://seu-backend.easypanel.host/health`

### **PASSO 3: Frontend (React)**
1. Crie um serviço App:
   - Nome: `loginui`
   - Source: GitHub
   - Repository: `seu-usuario/seu-repo`
   - Branch: `main`
   - Build: Nixpacks
   - Build Path: `/` ou `.`

2. Comandos Nixpacks:
   - Build: `npm run build`
   - Início: `npm run start`

3. Environment Variables:
   ```
   VITE_API_URL=https://seu-backend.easypanel.host
   NODE_VERSION=20.19.0
   ```

4. Domínios:
   - HTTPS: Ativado
   - Destino Protocolo: HTTP
   - Destino Porta: 3000
   - Caminho: /

5. Atualize `vite.config.ts` com seu domínio público em `allowedHosts`

6. Implante e teste: `https://seu-frontend.easypanel.host`

---

## ✅ Checklist Final

- [ ] PostgreSQL criado e schema executado
- [ ] Backend rodando e /health retorna 200 OK
- [ ] VITE_API_URL aponta para domínio público do backend
- [ ] vite.config.ts tem o domínio público em allowedHosts
- [ ] Frontend abrindo sem erro 502
- [ ] Login funcionando (email: teste@email.com, senha: 123456)

---

## 📝 Notas Importantes

1. **Variáveis de Ambiente:**
   - Frontend: `VITE_API_URL`, `NODE_VERSION`
   - Backend: DB_*, JWT_SECRET, PORT

2. **Domínios:**
   - Sempre use HTTPS (ativado no EasyPanel)
   - Porta interna: 3000
   - Protocolo interno: HTTP

3. **JWT_SECRET:**
   - Use uma chave forte e única
   - Nunca exponha no código

4. **Banco de Dados:**
   - Host interno: `postgres` (nome do serviço)
   - Não use localhost fora da máquina local

5. **Vite Preview:**
   - Sempre adicione `allowedHosts` com o domínio público
   - Porta deve ser 3000 no container

---

## 🔗 Endpoints da API

| Método | Endpoint | Descrição | Payload |
|--------|----------|-----------|---------|
| GET | `/health` | Verifica saúde da API | - |
| POST | `/api/auth/login` | Realiza login | `{email, senha}` |
| POST | `/api/auth/verify` | Valida token JWT | Header: `Authorization: Bearer <token>` |

---

**Criado em:** 20 de janeiro de 2026  
**Stack:** React 19 + Vite + Flask + PostgreSQL + Nixpacks
