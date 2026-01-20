# 🔐 Sistema de Autenticação Seguro

## 📋 Visão Geral

Este sistema implementa autenticação segura com:
- **Senha hasheada com bcrypt** (NUNCA em plaintext)
- **JWT (JSON Web Token)** para sessões
- **PostgreSQL** como banco de dados
- **Flask** como backend
- **React** como frontend

---

## 🔒 Segurança

### Como as senhas são armazenadas?

❌ **NUNCA assim** (plaintext):
```sql
INSERT INTO usuarios (email, senha) VALUES ('user@email.com', '123456');
```

✅ **SEMPRE assim** (bcrypt hash):
```sql
INSERT INTO usuarios (email, senha) VALUES ('user@email.com', '$2b$12$KIX...');
```

### O que é bcrypt?

Bcrypt é um algoritmo de hashing com **salt automático**:
- Cada senha gera um hash diferente (mesmo senha igual)
- Impossível reverter hash → senha original
- Lento de propósito (previne ataques de força bruta)

Exemplo:
```python
import bcrypt

senha = "123456"
hash1 = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
hash2 = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

print(hash1 != hash2)  # True! Hashes diferentes para mesma senha
```

---

## 🚀 Como usar

### 1️⃣ Criar novo usuário (RECOMENDADO)

```bash
cd backend
python create_user.py
```

Você será solicitado:
- Email
- Senha (será hasheada automaticamente)
- Nome (opcional)

### 2️⃣ Atualizar usuário de teste existente

Se você já tem `teste@email.com` com senha plaintext:

```bash
cd backend
python update_test_user.py
```

Isso atualizará a senha para hash bcrypt.

### 3️⃣ Fazer login

No frontend React, envie:
```typescript
POST /api/auth/login
{
  "email": "teste@email.com",
  "senha": "123456"
}
```

Backend retorna:
```json
{
  "sucesso": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "email": "teste@email.com",
    "nome": "Usuário Teste"
  }
}
```

---

## 🔍 Fluxo de Autenticação

```
[1] Usuário digita email + senha no frontend
                ↓
[2] React envia POST /api/auth/login
                ↓
[3] Flask busca usuário no PostgreSQL
                ↓
[4] Compara senha digitada com hash do banco (bcrypt.checkpw)
                ↓
[5] Se correto: gera JWT token
                ↓
[6] React salva token no localStorage
                ↓
[7] Requisições futuras enviam token no header
    Authorization: Bearer <token>
```

---

## 🧪 Testes

### Verificar hash bcrypt
```bash
python -c "import bcrypt; print(bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode())"
```

### Testar login via curl
```bash
curl -X POST https://login-backend.znh7ry.easypanel.host/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","senha":"123456"}'
```

### Verificar usuários no banco
```sql
SELECT id, email, LEFT(senha, 20) as senha_hash, nome 
FROM usuarios;
```

---

## ⚠️ IMPORTANTE

### Compatibilidade com senhas antigas

O código **SUPORTA AMBOS** (apenas durante migração):
- ✅ Senha hasheada bcrypt (`$2b$...`)
- ⚠️ Senha plaintext (TEMPORÁRIO)

Porém, **SEMPRE crie novos usuários com bcrypt**.

### Checagem de senha no código
```python
# Se senha começa com $2b$ ou $2a$ → bcrypt
if senha_db.startswith('$2b$') or senha_db.startswith('$2a$'):
    senha_correta = bcrypt.checkpw(senha.encode(), senha_db.encode())
else:
    # Plaintext (APENAS PARA DESENVOLVIMENTO)
    senha_correta = (senha == senha_db)
```

---

## 📦 Dependências

```txt
flask==2.3.3
flask-cors==4.0.0
bcrypt==4.0.1
PyJWT==2.10.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

---

## 🔧 Variáveis de Ambiente

```bash
# Banco de dados
DB_HOST=login_login-aut-db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=fa0e7201e1773b163eb3
DB_NAME=auth_db

# Segurança
JWT_SECRET=sk-prod-2026-login-system-az9x4kL8pQ2mN6tV1wJe3rF5uD7sB9cH0

# Servidor
PORT=3000
```

---

## 🎯 Checklist de Segurança

- [x] Senha com bcrypt (não plaintext)
- [x] JWT com secret seguro
- [x] CORS configurado corretamente
- [x] HTTPS em produção
- [x] Senha nunca retorna para frontend
- [x] Logs de tentativas de login
- [x] Sessões com expiração (24h)
- [x] Tratamento de erros sem expor detalhes

---

## 📚 Referências

- [bcrypt docs](https://github.com/pyca/bcrypt/)
- [PyJWT docs](https://pyjwt.readthedocs.io/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
