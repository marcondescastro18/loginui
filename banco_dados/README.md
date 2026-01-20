# 🗄️ Banco de Dados - Login System (PostgreSQL)

Documentação completa para configurar o banco de dados PostgreSQL usando EasyPanel.

## 📋 Índice

- [1. Criar Banco de Dados no EasyPanel](#1-criar-banco-de-dados-no-easypanel)
- [2. Executar Schema SQL](#2-executar-schema-sql)
- [3. Tabelas Criadas](#3-tabelas-criadas)
- [4. Variáveis de Ambiente](#4-variáveis-de-ambiente)
- [5. Conexão com Backend](#5-conexão-com-backend)
- [6. Operações Comuns](#6-operações-comuns)

---

## 1. Criar Banco de Dados no EasyPanel

### Passo 1: Acessar EasyPanel
1. Faça login em sua conta EasyPanel
2. Vá para **Serviços** → **Banco de Dados**
3. Clique em **Criar Novo Banco de Dados**

### Passo 2: Configurar PostgreSQL
- **Tipo:** PostgreSQL 14.0 (ou superior)
- **Nome do Banco:** `login_system`
- **Usuário:** `login_user`
- **Senha:** Gere uma senha forte (salve em local seguro!)
- **Replicação:** Desativada (para teste)
- **Backup:** Ativado (recomendado)

### Passo 3: Conexão
EasyPanel fornecerá:
- **Host:** seu-host-db.easypanel.host
- **Porta:** 5432 (padrão PostgreSQL)
- **Usuário:** login_user
- **Senha:** sua-senha-aqui
- **Database:** login_system

---

## 2. Executar Schema SQL

### Opção A: Via pgAdmin (Recomendado)
1. No EasyPanel, acesse **pgAdmin** para seu banco
2. Selecione o banco `login_system`
3. Vá para **Tools** → **Query Tool**
4. Cole o conteúdo do arquivo `schema.sql`
5. Clique em **Execute** (botão play)

### Opção B: Via Terminal SSH/PSQL
```bash
# Conectar ao banco
psql -h seu-host-db.easypanel.host -U login_user -d login_system < schema.sql

# Ou manualmente
psql -h seu-host-db.easypanel.host -U login_user -d login_system
# Digite a senha
# Cole os comandos do schema.sql
# \q para sair
```

### Opção C: Via Node.js (Backend)
```javascript
const { Pool } = require('pg');
const fs = require('fs');

const schema = fs.readFileSync('./schema.sql', 'utf-8');
const pool = new Pool({
  host: 'seu-host-db.easypanel.host',
  user: 'login_user',
  password: 'sua-senha',
  database: 'login_system'
});

// Executar schema
const client = await pool.connect();
try {
  await client.query(schema);
  console.log('✅ Schema criado com sucesso!');
} finally {
  client.release();
}
```

---

## 3. Tabelas Criadas

### 📊 Tabela: `usuarios`
Armazena as informações dos usuários.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | SERIAL | ID único (auto-incremento) |
| `email` | VARCHAR(255) | Email único do usuário |
| `senha` | VARCHAR(255) | Senha hashada (bcrypt) |
| `nome` | VARCHAR(255) | Nome completo |
| `ativo` | BOOLEAN | Se o usuário está ativo |
| `criado_em` | TIMESTAMP | Data de criação |
| `atualizado_em` | TIMESTAMP | Data de atualização |
| `ultimo_acesso` | TIMESTAMP | Último login |

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `email`
- INDEX: `idx_usuarios_email`, `idx_usuarios_ativo`

---

### 🔐 Tabela: `sessoes`
Armazena tokens e sessões ativas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | SERIAL | ID único |
| `usuario_id` | INT | ID do usuário (FK) |
| `token` | VARCHAR(500) | JWT ou token de sessão |
| `ip_address` | VARCHAR(50) | IP do cliente |
| `user_agent` | VARCHAR(255) | Browser/dispositivo |
| `expirado_em` | TIMESTAMP | Quando expira |
| `criado_em` | TIMESTAMP | Quando foi criado |

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `usuario_id` (ON DELETE CASCADE)
- INDEX: `idx_sessoes_token`, `idx_sessoes_usuario_id`, `idx_sessoes_expirado_em`

---

### 📝 Tabela: `logs_acesso`
Registra tentativas de login e eventos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | SERIAL | ID único |
| `usuario_id` | INT | ID do usuário (nullable) |
| `email` | VARCHAR(255) | Email tentado |
| `tipo_evento` | VARCHAR(50) | login, logout, erro |
| `ip_address` | VARCHAR(50) | IP da tentativa |
| `sucesso` | BOOLEAN | Login bem-sucedido? |
| `mensagem` | VARCHAR(255) | Descrição do evento |
| `criado_em` | TIMESTAMP | Quando ocorreu |

**Índices:**
- PRIMARY KEY: `id`
- INDEX: `idx_logs_usuario_id`, `idx_logs_criado_em`, `idx_logs_tipo_evento`

---

## 4. Variáveis de Ambiente

Adicione estas variáveis no EasyPanel ao criar a aplicação Node.js:

```env
# Banco de Dados PostgreSQL
DB_HOST=seu-host-db.easypanel.host
DB_PORT=5432
DB_USER=login_user
DB_PASSWORD=sua-senha-super-secreta
DB_DATABASE=login_system
DB_POOL_LIMIT=10

# JWT
JWT_SECRET=sua-chave-secreta-super-longa
JWT_EXPIRY=24h

# Node
NODE_ENV=production

# API
API_PORT=3000
API_HOST=0.0.0.0
```

---

## 5. Conexão com Backend

### Node.js + PostgreSQL (pg)
```javascript
// db.js
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  max: parseInt(process.env.DB_POOL_LIMIT || 10),
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

module.exports = pool;
```

### Instalar dependências
```bash
npm install pg bcrypt jsonwebtoken express
```

### Express + Login Route
```javascript
// routes/login.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../db');

const router = express.Router();

router.post('/login', async (req, res) => {
  const { email, senha } = req.body;
  
  try {
    // Buscar usuário
    const result = await pool.query(
      'SELECT * FROM usuarios WHERE email = $1 AND ativo = TRUE',
      [email]
    );
    
    const user = result.rows[0];
    
    if (!user) {
      await pool.query(
        'INSERT INTO logs_acesso (email, tipo_evento, ip_address, sucesso) VALUES ($1, $2, $3, $4)',
        [email, 'login', req.ip, false]
      );
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Validar senha
    const senhaValida = await bcrypt.compare(senha, user.senha);
    if (!senhaValida) {
      await pool.query(
        'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso) VALUES ($1, $2, $3, $4, $5)',
        [user.id, email, 'login', req.ip, false]
      );
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Gerar token
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRY }
    );
    
    // Criar sessão
    const expirado_em = new Date(Date.now() + 24 * 60 * 60 * 1000);
    await pool.query(
      'INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, expirado_em) VALUES ($1, $2, $3, $4, $5)',
      [user.id, token, req.ip, req.get('user-agent'), expirado_em]
    );
    
    // Log de sucesso
    await pool.query(
      'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso) VALUES ($1, $2, $3, $4, $5)',
      [user.id, email, 'login', req.ip, true]
    );
    
    // Atualizar último acesso
    await pool.query(
      'UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = $1',
      [user.id]
    );
    
    res.json({ token, user: { id: user.id, email: user.email, nome: user.nome } });
    
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Erro ao fazer login' });
  }
});

module.exports = router;
```

---

## 6. Operações Comuns (PostgreSQL)

### Criar Novo Usuário
```sql
-- Gerar hash bcrypt: bcrypt.hash('senha123', 10) em Node.js
INSERT INTO usuarios (email, nome, senha) 
VALUES ('novo@email.com', 'Novo Usuário', '$2b$10$hash_bcrypt_aqui');
```

### Atualizar Senha
```sql
UPDATE usuarios 
SET senha = '$2b$10$nova_senha_hash' 
WHERE id = 1;
```

### Desativar Usuário
```sql
UPDATE usuarios SET ativo = FALSE WHERE id = 1;
```

### Deletar Sessões Expiradas
```sql
DELETE FROM sessoes WHERE expirado_em < NOW();
```

### Relatório de Atividades
```sql
SELECT 
  u.email, 
  COUNT(l.id) as total_acessos,
  COUNT(CASE WHEN l.sucesso = TRUE THEN 1 END) as acessos_sucesso,
  COUNT(CASE WHEN l.sucesso = FALSE THEN 1 END) as acessos_erro,
  MAX(l.criado_em) as ultimo_acesso
FROM usuarios u
LEFT JOIN logs_acesso l ON u.id = l.usuario_id AND l.tipo_evento = 'login'
WHERE u.ativo = TRUE
GROUP BY u.id, u.email
ORDER BY total_acessos DESC;
```

### Usuários Ativos Hoje
```sql
SELECT DISTINCT u.id, u.email, u.nome, COUNT(*) as acessos_hoje
FROM usuarios u
INNER JOIN logs_acesso l ON u.id = l.usuario_id
WHERE DATE(l.criado_em) = CURRENT_DATE AND l.sucesso = TRUE
GROUP BY u.id, u.email, u.nome
ORDER BY acessos_hoje DESC;
```

---

## ⚠️ Segurança

### Senhas
- **NUNCA** armazene senhas em texto plano
- Use bcrypt com salt (min 10 rounds)
- Exemplo em Node.js:
  ```javascript
  const hash = await bcrypt.hash(senha, 10);
  ```

### JWT
- Use uma chave secreta forte (64+ caracteres)
- Guarde em variáveis de ambiente
- Defina expiração apropriada (24h recomendado)

### SQL Injection
- Use Parameterized Queries (já feito nos exemplos com $1, $2, etc)
- Nunca concatene inputs do usuário na query

### SSL/TLS
- Ative SSL em produção
- Configure no `db-config.js`

### Rate Limiting
```javascript
// Implementar limite de tentativas de login
// Exemplo: Máx 5 tentativas em 15 minutos
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 5, // 5 tentativas
  message: 'Muitas tentativas de login, tente mais tarde'
});

router.post('/login', loginLimiter, ...);
```

---

## 📊 Diferenças PostgreSQL vs MySQL

| Aspecto | PostgreSQL | MySQL |
|--------|-----------|-------|
| **Auto Increment** | SERIAL | AUTO_INCREMENT |
| **Booleans** | BOOLEAN | BOOLEAN/TINYINT |
| **Timestamps** | TIMESTAMP | TIMESTAMP |
| **Variáveis** | $1, $2, $3 | ?, ?, ? |
| **Operador de Adição** | INTERVAL | DATE_ADD() |
| **Índices** | CREATE INDEX | INDEX |
| **Foreign Keys** | CASCADE automático | Opcional |

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar permissões do usuário:** 
   ```sql
   SELECT * FROM information_schema.role_table_grants 
   WHERE grantee = 'login_user';
   ```

2. **Testar conexão:**
   ```bash
   psql -h seu-host -U login_user -d login_system
   ```

3. **Verificar logs EasyPanel**
   - Vá em **Aplicações** → Sua App → **Logs**

4. **Ver conexões ativas:**
   ```sql
   SELECT pid, usename, application_name, state 
   FROM pg_stat_activity 
   WHERE datname = 'login_system';
   ```

---

**Data de criação:** 19 de janeiro de 2026
**Versão:** 1.0 (PostgreSQL)
**Status:** Pronto para Produção ✅
**Banco de Dados:** PostgreSQL 14+

---

## 2. Executar Schema SQL

### Opção A: Via phpMyAdmin (Recomendado)
1. No EasyPanel, acesse **phpMyAdmin** para seu banco
2. Selecione o banco `login_system`
3. Vá para a aba **SQL**
4. Cole o conteúdo do arquivo `schema.sql`
5. Clique em **Executar**

### Opção B: Via Terminal SSH
```bash
# Conectar ao banco
mysql -h seu-host-db.easypanel.host -u login_user -p login_system < schema.sql

# Ou manualmente
mysql -h seu-host-db.easypanel.host -u login_user -p
# Digite a senha
# Cole os comandos do schema.sql
```

### Opção C: Via Node.js (Backend)
```javascript
const mysql = require('mysql2/promise');
const fs = require('fs');

const schema = fs.readFileSync('./schema.sql', 'utf-8');
const connection = await mysql.createConnection({
  host: 'seu-host-db.easypanel.host',
  user: 'login_user',
  password: 'sua-senha',
  database: 'login_system'
});

await connection.query(schema);
console.log('✅ Schema criado com sucesso!');
```

---

## 3. Tabelas Criadas

### 📊 Tabela: `usuarios`
Armazena as informações dos usuários.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID único (auto-incremento) |
| `email` | VARCHAR(255) | Email único do usuário |
| `senha` | VARCHAR(255) | Senha hashada (bcrypt) |
| `nome` | VARCHAR(255) | Nome completo |
| `ativo` | BOOLEAN | Se o usuário está ativo |
| `criado_em` | TIMESTAMP | Data de criação |
| `atualizado_em` | TIMESTAMP | Data de atualização |
| `ultimo_acesso` | TIMESTAMP | Último login |

**Índices:**
- PRIMARY KEY: `id`
- UNIQUE: `email`
- INDEX: `email`, `ativo`

---

### 🔐 Tabela: `sessoes`
Armazena tokens e sessões ativas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID único |
| `usuario_id` | INT | ID do usuário (FK) |
| `token` | VARCHAR(500) | JWT ou token de sessão |
| `ip_address` | VARCHAR(50) | IP do cliente |
| `user_agent` | VARCHAR(255) | Browser/dispositivo |
| `expirado_em` | TIMESTAMP | Quando expira |
| `criado_em` | TIMESTAMP | Quando foi criado |

**Índices:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `usuario_id`
- INDEX: `token`, `usuario_id`, `expirado_em`

---

### 📝 Tabela: `logs_acesso`
Registra tentativas de login e eventos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INT | ID único |
| `usuario_id` | INT | ID do usuário (nullable) |
| `email` | VARCHAR(255) | Email tentado |
| `tipo_evento` | VARCHAR(50) | login, logout, erro |
| `ip_address` | VARCHAR(50) | IP da tentativa |
| `sucesso` | BOOLEAN | Login bem-sucedido? |
| `mensagem` | VARCHAR(255) | Descrição do evento |
| `criado_em` | TIMESTAMP | Quando ocorreu |

**Índices:**
- PRIMARY KEY: `id`
- INDEX: `usuario_id`, `criado_em`, `tipo_evento`

---

## 4. Variáveis de Ambiente

Adicione estas variáveis no EasyPanel ao criar a aplicação Node.js:

```env
# Banco de Dados MySQL
DB_HOST=seu-host-db.easypanel.host
DB_PORT=3306
DB_USER=login_user
DB_PASSWORD=sua-senha-super-secreta
DB_DATABASE=login_system
DB_POOL_LIMIT=10

# JWT
JWT_SECRET=sua-chave-secreta-super-longa
JWT_EXPIRY=24h

# Node
NODE_ENV=production

# API
API_PORT=3000
API_HOST=0.0.0.0
```

---

## 5. Conexão com Backend

### Node.js + MySQL2
```javascript
// db.js
const mysql = require('mysql2/promise');

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  waitForConnections: true,
  connectionLimit: parseInt(process.env.DB_POOL_LIMIT || 10),
  queueLimit: 0,
  enableKeepAlive: true,
  keepAliveInitialDelayMs: 0,
});

module.exports = pool;
```

### Express + Login Route
```javascript
// routes/login.js
const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const pool = require('../db');

const router = express.Router();

router.post('/login', async (req, res) => {
  const { email, senha } = req.body;
  
  try {
    const connection = await pool.getConnection();
    
    // Buscar usuário
    const [users] = await connection.query(
      'SELECT * FROM usuarios WHERE email = ? AND ativo = TRUE',
      [email]
    );
    
    if (users.length === 0) {
      await connection.query(
        'INSERT INTO logs_acesso (email, tipo_evento, ip_address, sucesso) VALUES (?, ?, ?, ?)',
        [email, 'login', req.ip, false]
      );
      connection.release();
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    const user = users[0];
    
    // Validar senha
    const senhaValida = await bcrypt.compare(senha, user.senha);
    if (!senhaValida) {
      await connection.query(
        'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso) VALUES (?, ?, ?, ?, ?)',
        [user.id, email, 'login', req.ip, false]
      );
      connection.release();
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Gerar token
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRY }
    );
    
    // Criar sessão
    const expirado_em = new Date(Date.now() + 24 * 60 * 60 * 1000);
    await connection.query(
      'INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, expirado_em) VALUES (?, ?, ?, ?, ?)',
      [user.id, token, req.ip, req.get('user-agent'), expirado_em]
    );
    
    // Log de sucesso
    await connection.query(
      'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso) VALUES (?, ?, ?, ?, ?)',
      [user.id, email, 'login', req.ip, true]
    );
    
    // Atualizar último acesso
    await connection.query(
      'UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = ?',
      [user.id]
    );
    
    connection.release();
    res.json({ token, user: { id: user.id, email: user.email, nome: user.nome } });
    
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Erro ao fazer login' });
  }
});

module.exports = router;
```

---

## 6. Operações Comuns

### Criar Novo Usuário
```sql
INSERT INTO usuarios (email, nome, senha) 
VALUES ('novo@email.com', 'Novo Usuário', UNHEX(SHA2('senha123', 256)));
```

### Atualizar Senha
```sql
UPDATE usuarios 
SET senha = UNHEX(SHA2('nova_senha', 256)) 
WHERE id = 1;
```

### Desativar Usuário
```sql
UPDATE usuarios SET ativo = FALSE WHERE id = 1;
```

### Deletar Sessões Expiradas
```sql
DELETE FROM sessoes WHERE expirado_em < NOW();
```

### Relatório de Atividades
```sql
SELECT 
  u.email, 
  COUNT(l.id) as total_acessos,
  SUM(CASE WHEN l.sucesso = TRUE THEN 1 ELSE 0 END) as acessos_sucesso,
  SUM(CASE WHEN l.sucesso = FALSE THEN 1 ELSE 0 END) as acessos_erro,
  MAX(l.criado_em) as ultimo_acesso
FROM usuarios u
LEFT JOIN logs_acesso l ON u.id = l.usuario_id AND l.tipo_evento = 'login'
GROUP BY u.id;
```

---

## ⚠️ Segurança

### Senhas
- **NUNCA** armazene senhas em texto plano
- Use bcrypt com salt (min 10 rounds)
- Exemplo: `password_hash('senha', PASSWORD_BCRYPT);`

### JWT
- Use uma chave secreta forte (64+ caracteres)
- Guarde em variáveis de ambiente
- Defina expiração apropriada (24h recomendado)

### SQL Injection
- Use prepared statements (já feito nos exemplos)
- Nunca concatene inputs do usuário na query

### Rate Limiting
```javascript
// Implementar limite de tentativas de login
// Exemplo: Máx 5 tentativas em 15 minutos
```

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar permissões do usuário:** 
   ```sql
   SHOW GRANTS FOR 'login_user'@'%';
   ```

2. **Testar conexão:**
   ```bash
   mysql -h seu-host -u login_user -p
   ```

3. **Verificar logs EasyPanel**
   - Vá em **Aplicações** → Sua App → **Logs**

---

**Data de criação:** 19 de janeiro de 2026
**Versão:** 1.0
**Status:** Pronto para Produção ✅
