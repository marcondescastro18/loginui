# ⚡ Guia Rápido - Setup em 10 Minutos

Para criar um projeto similar do zero, siga estes passos:

---

## 🚀 Setup Completo

### 1️⃣ Criar Projeto Frontend (2 min)

```bash
# Criar projeto Vite + React + TypeScript
npm create vite@latest login-ui -- --template react-ts
cd login-ui
npm install

# Instalar dependências
npm install react-router-dom axios
```

### 2️⃣ Criar Backend Flask (2 min)

```bash
# Criar pasta backend
mkdir backend
cd backend

# Criar requirements.txt
cat > requirements.txt << EOF
Flask==2.3.3
psycopg2-binary==2.9.9
PyJWT==2.10.1
bcrypt==4.0.1
python-dotenv==1.0.0
flask-cors==4.0.0
gunicorn==21.2.0
EOF

# Instalar
pip install -r requirements.txt
```

### 3️⃣ Configurar PostgreSQL (2 min)

```bash
# Conectar ao PostgreSQL
psql -U postgres

# Executar no psql:
CREATE DATABASE login_system;
\c login_system

CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessoes (
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  endereco_ip VARCHAR(50),
  expirado_em TIMESTAMP NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE registros_acesso (
  id SERIAL PRIMARY KEY,
  usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo_evento VARCHAR(50),
  endereco_ip VARCHAR(50),
  sucesso BOOLEAN,
  mensagem VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Criar usuário teste (senha: 123456)
INSERT INTO usuarios (email, senha) VALUES 
('teste@email.com', '$2b$10$N9qo8uLOickgx2ZMRZoMye');
```

### 4️⃣ Criar Arquivos Backend (2 min)

**backend/config.py:**
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

**backend/.env:**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=login_system
DB_USER=postgres
DB_PASSWORD=sua_senha
JWT_SECRET=chave_secreta_minimo_32_caracteres_aqui
PORT=5000
DEBUG=True
```

**backend/db.py:** (copiar do repositório ou README.md)

**backend/app.py:** (copiar do repositório ou README.md)

### 5️⃣ Criar Frontend (2 min)

**src/services/api.ts:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: { 'Content-Type': 'application/json' },
});

export default api;
```

**src/pages/Login.tsx:** (copiar do repositório)

**src/pages/Success.tsx:** (copiar do repositório)

**src/App.tsx:**
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

---

## ✅ Testar (1 min)

### Terminal 1 - Backend:
```bash
cd backend
python app.py
# Rodando em http://localhost:5000
```

### Terminal 2 - Frontend:
```bash
npm run dev
# Rodando em http://localhost:3000
```

### Testar Login:
- Email: `teste@email.com`
- Senha: `123456`

---

## 🎯 Arquivos Essenciais

```
login-ui/
├── backend/
│   ├── .env              # ⚠️ Configurações (não commitar)
│   ├── app.py            # 📌 API endpoints
│   ├── db.py             # 📌 Funções de banco
│   ├── config.py         # 📌 Configurações
│   └── requirements.txt  # 📌 Dependências Python
│
├── src/
│   ├── services/
│   │   └── api.ts        # 📌 Cliente HTTP
│   ├── pages/
│   │   ├── Login.tsx     # 📌 Página de login
│   │   └── Success.tsx   # 📌 Página pós-login
│   └── App.tsx           # 📌 Rotas
│
├── package.json          # 📌 Dependências Node
└── vite.config.ts        # 📌 Config Vite
```

---

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Backend
cd backend && python app.py

# Frontend
npm run dev
```

### Build Produção
```bash
npm run build
```

### Testes
```bash
# Testar backend
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","senha":"123456"}'

# Deve retornar: {"sucesso": true, "token": "..."}
```

### Criar Novo Usuário
```python
# backend/create_user.py
import bcrypt
import psycopg2

senha = input("Senha: ")
hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

conn = psycopg2.connect(
    host="localhost",
    database="login_system",
    user="postgres",
    password="sua_senha"
)
cur = conn.cursor()
cur.execute(
    "INSERT INTO usuarios (email, senha) VALUES (%s, %s)",
    (input("Email: "), hash_senha)
)
conn.commit()
print("✅ Usuário criado!")
```

---

## ⚠️ Checklist de Segurança

Antes de fazer deploy:

- [ ] JWT_SECRET com 32+ caracteres aleatórios
- [ ] Senhas sempre com bcrypt (nunca plaintext)
- [ ] HTTPS em produção
- [ ] CORS configurado corretamente
- [ ] .env no .gitignore
- [ ] Validação de inputs
- [ ] Rate limiting (recomendado)
- [ ] Logs de auditoria ativos

---

## 🚢 Deploy Rápido

### EasyPanel (Mais Fácil)

1. Criar 3 recursos:
   - PostgreSQL (banco)
   - Python App (backend)
   - Node App (frontend)

2. Configurar variáveis de ambiente

3. Deploy automático via Git

### Heroku

```bash
# Backend
heroku create app-backend
heroku addons:create heroku-postgresql:mini
git push heroku main

# Frontend
heroku create app-frontend
git push heroku main
```

---

## 📚 Documentação Completa

Ver `README.md` para:
- Arquitetura detalhada
- Troubleshooting
- Exemplos de código
- Segurança avançada
- Scripts úteis

---

## 💡 Dicas

1. **Sempre use variáveis de ambiente** para dados sensíveis
2. **Teste localmente** antes de fazer deploy
3. **Faça backup** do banco de dados
4. **Use Git** para versionamento
5. **Documente** as mudanças que fizer

---

**Tempo total:** ~10 minutos  
**Nível:** Iniciante/Intermediário  
**Resultado:** Sistema de login funcional e seguro

✅ **Pronto para começar!**
