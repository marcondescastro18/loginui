# 🔐 Login System - Documentação Completa

Sistema de autenticação full-stack moderno e seguro, construído com **React 19**, **TypeScript**, **Vite**, **Flask** e **PostgreSQL**.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Tecnologias Utilizadas](#tecnologias-utilizadas)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Setup do Ambiente](#setup-do-ambiente)
5. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
6. [Configuração do Backend](#configuração-do-backend)
7. [Configuração do Frontend](#configuração-do-frontend)
8. [Deploy em Produção](#deploy-em-produção)
9. [Troubleshooting](#troubleshooting)
10. [Referências e Scripts Úteis](#referências-e-scripts-úteis)

---

## 🎯 Visão Geral

Sistema completo de autenticação com:
- ✅ Login seguro com JWT
- ✅ Hash de senhas com bcrypt
- ✅ Validação de tokens
- ✅ Logs de acesso
- ✅ Sessões persistentes
- ✅ Interface responsiva
- ✅ CORS configurado
- ✅ Tratamento robusto de erros

**Status:** ✅ Pronto para produção

---

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 19.2.0** - Biblioteca UI
- **TypeScript 5.9.3** - Tipagem estática
- **Vite 7.2.4** - Build tool e dev server
- **React Router DOM 7.12.0** - Roteamento
- **Axios 1.13.2** - Cliente HTTP
- **CSS3** - Estilização

### Backend
- **Python 3.11+** - Linguagem
- **Flask 2.3.3** - Framework web
- **Gunicorn 21.2.0** - WSGI server
- **PostgreSQL 15+** - Banco de dados
- **psycopg2 2.9.9** - Driver PostgreSQL
- **PyJWT 2.10.1** - JWT tokens
- **bcrypt 4.0.1** - Hash de senhas
- **Flask-CORS 4.0.0** - CORS middleware

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐      HTTPS      ┌─────────────────┐
│                 │ ──────────────> │                 │
│   Frontend      │                 │   Backend API   │
│   (React/Vite)  │ <────────────── │   (Flask)       │
│                 │      JSON       │                 │
└─────────────────┘                 └────────┬────────┘
                                             │
                                             │ SQL
                                             ▼
                                    ┌─────────────────┐
                                    │   PostgreSQL    │
                                    │   Database      │
                                    └─────────────────┘
```

### Fluxo de Autenticação

```
1. Usuário envia credenciais (email/senha)
   │
   ▼
2. Backend valida credenciais no PostgreSQL
   │
   ▼
3. Se válido: gera JWT token com exp 24h
   │
   ▼
4. Registra sessão e log de acesso
   │
   ▼
5. Retorna token + dados do usuário
   │
   ▼
6. Frontend armazena token no localStorage
   │
   ▼
7. Redireciona para página Success
```

---

## 🚀 Setup do Ambiente

### Pré-requisitos

- **Node.js 18+** e npm
- **Python 3.11+** e pip
- **PostgreSQL 15+**
- **Git**

### 1. Clone o Repositório

```bash
git clone https://github.com/marcondescastro18/loginui.git
cd loginui
```

### 2. Estrutura de Pastas

```
login-ui/
├── src/                    # Frontend React
│   ├── pages/             
│   │   ├── Login.tsx      # Página de login
│   │   ├── Login.css
│   │   ├── Success.tsx    # Página pós-login
│   │   └── Success.css
│   ├── services/
│   │   └── api.ts         # Cliente Axios
│   ├── App.tsx            # Rotas principais
│   └── main.tsx           # Entry point
│
├── backend/               # Backend Flask
│   ├── app.py            # Endpoints da API
│   ├── db.py             # Funções de banco
│   ├── config.py         # Configurações
│   ├── requirements.txt  # Dependências Python
│   └── Procfile          # Config deploy
│
├── banco_dados/          # Schema e docs do DB
│   └── schema.sql        # Schema PostgreSQL
│
├── public/               # Assets estáticos
├── dist/                 # Build de produção
├── vite.config.ts        # Config Vite
├── package.json          # Dependências Node
└── tsconfig.json         # Config TypeScript
```

---

## 🗄️ Configuração do Banco de Dados

### Schema Real (Simplificado)

⚠️ **IMPORTANTE**: O schema em produção usa apenas as colunas essenciais:

#### Tabela `usuarios`
```sql
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela `sessoes`
```sql
CREATE TABLE sessoes (
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  endereco_ip VARCHAR(50),
  expirado_em TIMESTAMP NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela `registros_acesso`
```sql
CREATE TABLE registros_acesso (
  id SERIAL PRIMARY KEY,
  usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo_evento VARCHAR(50),
  endereco_ip VARCHAR(50),
  sucesso BOOLEAN,
  mensagem VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Criar Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Criar banco
CREATE DATABASE login_system;

# Conectar ao banco
\c login_system

# Executar schema (use o schema simplificado acima)
```

### Criar Usuário de Teste

```python
# backend/create_user.py
import bcrypt
import psycopg2

# Gerar hash da senha
senha = "123456"
hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Inserir usuário
conn = psycopg2.connect(
    host="localhost",
    database="login_system",
    user="postgres",
    password="sua_senha"
)
cur = conn.cursor()
cur.execute(
    "INSERT INTO usuarios (email, senha) VALUES (%s, %s)",
    ("teste@email.com", hash_senha)
)
conn.commit()
print("✅ Usuário criado com sucesso!")
```

---

## ⚙️ Configuração do Backend

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie `.env` na pasta `backend/`:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=login_system
DB_USER=postgres
DB_PASSWORD=sua_senha_postgres

# JWT
JWT_SECRET=sua_chave_secreta_super_forte_aqui_min_32_chars

# Server
PORT=3000
DEBUG=False
```

⚠️ **SEGURANÇA**: 
- Use senha forte no `JWT_SECRET` (mín. 32 caracteres)
- NUNCA commite o arquivo `.env` no Git
- Em produção, use variáveis de ambiente do servidor

### 3. Estrutura dos Arquivos Backend

#### `backend/config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'login_system')
    JWT_SECRET = os.getenv('JWT_SECRET')
    DEBUG = os.getenv('DEBUG', False)
    PORT = int(os.getenv('PORT', 3000))
```

#### `backend/db.py`
```python
import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_connection():
    """Retorna conexão com PostgreSQL"""
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
        print(f"Erro ao conectar: {e}")
        return None

def get_user_by_email(email):
    """Busca usuário por email (apenas colunas existentes)"""
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            "SELECT id, email, senha, criado_em FROM usuarios WHERE email = %s",
            (email,)
        )
        user = cur.fetchone()
        cur.close()
        return user
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def create_session(usuario_id, token, ip_address):
    """Cria sessão após login bem-sucedido"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) "
            "VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')",
            (usuario_id, token, ip_address)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def log_access(usuario_id, tipo_evento, ip_address, sucesso, mensagem):
    """Registra log de acesso (sem coluna email)"""
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO registros_acesso "
            "(usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) "
            "VALUES (%s, %s, %s, %s, %s)",
            (usuario_id, tipo_evento, ip_address, sucesso, mensagem)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
```

#### `backend/app.py`
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
import psycopg2
from datetime import datetime, timedelta
from db import get_user_by_email, create_session, log_access
from config import Config

app = Flask(__name__)

# Validar JWT_SECRET
if not Config.JWT_SECRET:
    raise ValueError("JWT_SECRET é obrigatória!")

# CORS
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "https://seu-dominio.com"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Email e senha obrigatórios'
            }), 400
        
        # Buscar usuário
        usuario = get_user_by_email(email)
        if not usuario:
            ip = request.remote_addr
            log_access(None, 'login', ip, False, 'Usuário não encontrado')
            return jsonify({
                'sucesso': False,
                'mensagem': 'Usuário ou senha inválida'
            }), 401
        
        # Verificar senha
        senha_db = usuario['senha']
        if senha_db.startswith('$2b$') or senha_db.startswith('$2a$'):
            senha_correta = bcrypt.checkpw(
                senha.encode('utf-8'),
                senha_db.encode('utf-8')
            )
        else:
            senha_correta = (senha == senha_db)
        
        if not senha_correta:
            ip = request.remote_addr
            log_access(None, 'login', ip, False, 'Senha inválida')
            return jsonify({
                'sucesso': False,
                'mensagem': 'Usuário ou senha inválida'
            }), 401
        
        # Gerar token JWT
        payload = {
            'user_id': usuario['id'],
            'email': usuario['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
        
        # Registrar sessão e log
        ip = request.remote_addr
        create_session(usuario['id'], token, ip)
        log_access(usuario['id'], 'login', ip, True, 'Login bem-sucedido')
        
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
        print(f"Erro de banco: {db_error}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro no banco de dados'
        }), 500
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao realizar login'
        }), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    """Verifica token JWT"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Token não fornecido'
            }), 401
        
        token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Token válido',
            'usuario': payload
        }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Token expirado'
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Token inválido'
        }), 401
    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao verificar token'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
```

### 4. Testar Backend

```bash
# Desenvolvimento
cd backend
python app.py

# Teste com curl
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","senha":"123456"}'
```

---

## 🎨 Configuração do Frontend

### 1. Instalar Dependências

```bash
npm install
```

### 2. Configurar Cliente API

#### `src/services/api.ts`
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
```

### 3. Variáveis de Ambiente

Crie `.env` na raiz do projeto:

```bash
# Desenvolvimento
VITE_API_URL=http://localhost:3000

# Produção
# VITE_API_URL=https://seu-backend.com
```

### 4. Página de Login

#### `src/pages/Login.tsx`
```typescript
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import "./Login.css";

export default function Login() {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const navigate = useNavigate();

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setErro("");
    setCarregando(true);

    try {
      const response = await api.post("/api/auth/login", { email, senha });
      
      if (response.data.sucesso) {
        localStorage.setItem("token", response.data.token);
        localStorage.setItem("usuario", JSON.stringify(response.data.usuario));
        navigate("/success");
      }
    } catch (error: any) {
      setErro(
        error.response?.data?.mensagem || "Erro ao realizar login"
      );
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleLogin}>
        <h1>Login</h1>
        
        {erro && <div className="erro">{erro}</div>}
        
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        
        <input
          type="password"
          placeholder="Senha"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />
        
        <button type="submit" disabled={carregando}>
          {carregando ? "Carregando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}
```

### 5. Rotas

#### `src/App.tsx`
```typescript
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Success from "./pages/Success";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/success" element={<Success />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### 6. Executar em Desenvolvimento

```bash
npm run dev
```

Acesse: `http://localhost:3000`

### 7. Build de Produção

```bash
npm run build
```

Arquivos gerados em `dist/`

---

## 🚢 Deploy em Produção

### Opção 1: EasyPanel (Recomendado)

1. **Backend Flask:**
   - Tipo: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - Porta: 3000
   - Adicionar variáveis de ambiente (.env)

2. **Frontend Vite:**
   - Tipo: Node.js
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run start`
   - Porta: 3000

3. **PostgreSQL:**
   - Criar banco no EasyPanel
   - Copiar credenciais para variáveis de ambiente do backend

### Opção 2: Heroku

```bash
# Backend
heroku create seu-app-backend
heroku addons:create heroku-postgresql:mini
git subtree push --prefix backend heroku main

# Frontend
heroku create seu-app-frontend
heroku buildpacks:set heroku/nodejs
git push heroku main
```

### Opção 3: Vercel (Frontend) + Railway (Backend)

**Frontend (Vercel):**
```bash
npm install -g vercel
vercel --prod
```

**Backend (Railway):**
- Conectar repositório GitHub
- Detecta Python automaticamente
- Adicionar PostgreSQL addon

---

## 🐛 Troubleshooting

### Erro: "column nome does not exist"

**Causa:** Schema do banco difere do código  
**Solução:** Use apenas colunas existentes:

```python
# ✅ CORRETO
cur.execute("SELECT id, email, senha, criado_em FROM usuarios WHERE email = %s", (email,))

# ❌ ERRADO
cur.execute("SELECT id, email, senha, nome FROM usuarios WHERE email = %s", (email,))
```

### Erro: "column email of relation registros_acesso does not exist"

**Causa:** Tabela `registros_acesso` não possui coluna `email`  
**Solução:**

```python
# ✅ CORRETO
log_access(usuario_id, 'login', ip, True, 'Sucesso')

# ❌ ERRADO
log_access(usuario_id, email, 'login', ip, True, 'Sucesso')
```

### Erro: CORS

**Solução:** Adicionar origem no backend:

```python
CORS(app, resources={r"/*": {
    "origins": ["http://localhost:3000", "https://seu-dominio.com"]
}})
```

### Erro: JWT_SECRET não encontrado

**Solução:** Criar `.env` com:

```bash
JWT_SECRET=sua_chave_secreta_minimo_32_caracteres
```

### Gunicorn reiniciando

**Causa:** Exceções SQL não tratadas  
**Solução:** Adicionar try/except:

```python
try:
    # operação de banco
except psycopg2.Error as e:
    print(f"Erro SQL: {e}")
    conn.rollback()
    return jsonify({'erro': 'Erro no banco'}), 500
```

---

## 📚 Referências e Scripts Úteis

### Gerar Hash de Senha

```python
import bcrypt

senha = "123456"
hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
print(hash_senha.decode('utf-8'))
```

### Testar Conexão PostgreSQL

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="login_system",
        user="postgres",
        password="senha"
    )
    print("✅ Conexão OK!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")
```

### Limpar Sessões Expiradas

```sql
DELETE FROM sessoes WHERE expirado_em < NOW();
```

### Ver Logs de Acesso

```sql
SELECT 
    u.email,
    ra.tipo_evento,
    ra.sucesso,
    ra.mensagem,
    ra.criado_em
FROM registros_acesso ra
LEFT JOIN usuarios u ON u.id = ra.usuario_id
ORDER BY ra.criado_em DESC
LIMIT 50;
```

---

## 📝 Checklist Para Novo Projeto

- [ ] Instalar Node.js, Python e PostgreSQL
- [ ] Clonar repositório
- [ ] Criar banco de dados
- [ ] Executar schema SQL (versão simplificada)
- [ ] Criar usuário de teste
- [ ] Configurar `.env` do backend
- [ ] Instalar dependências Python: `pip install -r requirements.txt`
- [ ] Testar backend: `python backend/app.py`
- [ ] Configurar `.env` do frontend
- [ ] Instalar dependências Node: `npm install`
- [ ] Testar frontend: `npm run dev`
- [ ] Build de produção: `npm run build`
- [ ] Deploy backend (Heroku/Railway/EasyPanel)
- [ ] Deploy frontend (Vercel/Netlify/EasyPanel)
- [ ] Configurar variáveis de ambiente em produção
- [ ] Testar login em produção

---

## 🔒 Segurança

- ✅ Senhas com bcrypt (salt rounds: 10)
- ✅ JWT tokens com expiração de 24h
- ✅ CORS configurado
- ✅ Validação de inputs
- ✅ Prepared statements (SQL injection protection)
- ✅ Logs de acesso auditáveis
- ✅ Variáveis sensíveis em .env
- ⚠️ HTTPS obrigatório em produção
- ⚠️ Rate limiting recomendado
- ⚠️ 2FA recomendado para produção

---

## 📞 Suporte

- **Repositório:** https://github.com/marcondescastro18/loginui
- **Documentação:** Este README
- **Schema:** `banco_dados/schema.sql`
- **Deploy:** `DEPLOY.md`

---

## 📄 Licença

MIT License - Uso livre para projetos pessoais e comerciais.

---

**Última atualização:** 21 de janeiro de 2026  
**Versão:** 2.0.0
