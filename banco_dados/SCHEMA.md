# 🔍 Schema do Banco de Dados - Documentação Completa

**Data:** 21 de janeiro de 2026  
**Banco:** PostgreSQL 15+  
**Versão Schema:** 2.0 (Simplificado)

---

## ⚠️ IMPORTANTE: Schema Real em Produção

O schema em produção usa **apenas as colunas essenciais**. Não inclui colunas adicionais como `nome`, `ativo`, `atualizado_em`, `ultimo_acesso`, etc.

---

## 📊 Tabelas

### 1. `usuarios`

Armazena credenciais e dados básicos dos usuários.

```sql
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT email_not_empty CHECK (email != '')
);

-- Índices
CREATE INDEX idx_usuarios_email ON usuarios(email);
```

#### Colunas:

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| `id` | SERIAL | NO | auto | ID único do usuário |
| `email` | VARCHAR(255) | NO | - | Email (único, usado no login) |
| `senha` | VARCHAR(255) | NO | - | Hash bcrypt da senha |
| `criado_em` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Data de criação |

#### Constraints:
- **PRIMARY KEY:** `id`
- **UNIQUE:** `email`
- **CHECK:** `email != ''`

#### Exemplo de Insert:

```sql
-- Com hash bcrypt
INSERT INTO usuarios (email, senha) 
VALUES ('teste@email.com', '$2b$10$N9qo8uLOickgx2ZMRZoMye');

-- Gerar hash em Python:
import bcrypt
hash = bcrypt.hashpw('123456'.encode(), bcrypt.gensalt()).decode()
```

---

### 2. `sessoes`

Armazena tokens JWT e sessões ativas.

```sql
CREATE TABLE sessoes (
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  endereco_ip VARCHAR(50),
  expirado_em TIMESTAMP NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT token_not_empty CHECK (token != '')
);

-- Índices
CREATE INDEX idx_sessoes_token ON sessoes(token);
CREATE INDEX idx_sessoes_usuario_id ON sessoes(usuario_id);
CREATE INDEX idx_sessoes_expirado_em ON sessoes(expirado_em);
```

#### Colunas:

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| `id` | SERIAL | NO | auto | ID único da sessão |
| `usuario_id` | INT | NO | - | FK para usuarios(id) |
| `token` | VARCHAR(500) | NO | - | Token JWT (único) |
| `endereco_ip` | VARCHAR(50) | YES | NULL | IP do cliente |
| `expirado_em` | TIMESTAMP | NO | - | Data/hora de expiração |
| `criado_em` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Data de criação |

#### Constraints:
- **PRIMARY KEY:** `id`
- **FOREIGN KEY:** `usuario_id` → `usuarios(id)` ON DELETE CASCADE
- **UNIQUE:** `token`
- **CHECK:** `token != ''`

#### Exemplo de Insert:

```sql
-- Após login bem-sucedido
INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) 
VALUES (1, 'eyJhbGciOiJIUzI1NiIs...', '192.168.1.100', NOW() + INTERVAL '24 hours');
```

---

### 3. `registros_acesso`

Logs de auditoria de tentativas de login e acessos.

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

-- Índices
CREATE INDEX idx_registros_usuario_id ON registros_acesso(usuario_id);
CREATE INDEX idx_registros_criado_em ON registros_acesso(criado_em);
CREATE INDEX idx_registros_tipo_evento ON registros_acesso(tipo_evento);
```

#### Colunas:

| Coluna | Tipo | Nullable | Default | Descrição |
|--------|------|----------|---------|-----------|
| `id` | SERIAL | NO | auto | ID único do log |
| `usuario_id` | INT | YES | NULL | FK para usuarios(id) (NULL se login falhou) |
| `tipo_evento` | VARCHAR(50) | YES | NULL | Tipo: 'login', 'logout', etc |
| `endereco_ip` | VARCHAR(50) | YES | NULL | IP do cliente |
| `sucesso` | BOOLEAN | YES | NULL | TRUE = sucesso, FALSE = falha |
| `mensagem` | VARCHAR(255) | YES | NULL | Mensagem descritiva |
| `criado_em` | TIMESTAMP | NO | CURRENT_TIMESTAMP | Data/hora do evento |

#### Constraints:
- **PRIMARY KEY:** `id`
- **FOREIGN KEY:** `usuario_id` → `usuarios(id)` ON DELETE SET NULL

#### Exemplos de Insert:

```sql
-- Login bem-sucedido
INSERT INTO registros_acesso (usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) 
VALUES (1, 'login', '192.168.1.100', TRUE, 'Login bem-sucedido');

-- Login falhado (usuário não encontrado)
INSERT INTO registros_acesso (usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) 
VALUES (NULL, 'login', '192.168.1.100', FALSE, 'Usuário não encontrado');

-- Senha inválida
INSERT INTO registros_acesso (usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) 
VALUES (NULL, 'login', '192.168.1.100', FALSE, 'Senha inválida');
```

---

## 🔗 Relacionamentos

```
usuarios (1) ──< (N) sessoes
    │
    └──< (N) registros_acesso
```

- Um usuário pode ter múltiplas sessões ativas
- Um usuário pode ter múltiplos registros de acesso
- Registros de acesso podem ter `usuario_id = NULL` (tentativas falhadas)

---

## 📋 Script de Criação Completo

```sql
-- =====================================================
-- Login System Database Schema v2.0
-- PostgreSQL 15+
-- =====================================================

-- Criar banco
CREATE DATABASE login_system;

-- Conectar ao banco
\c login_system

-- Tabela de usuários
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  senha VARCHAR(255) NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT email_not_empty CHECK (email != '')
);

CREATE INDEX idx_usuarios_email ON usuarios(email);

-- Tabela de sessões
CREATE TABLE sessoes (
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  token VARCHAR(500) UNIQUE NOT NULL,
  endereco_ip VARCHAR(50),
  expirado_em TIMESTAMP NOT NULL,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT token_not_empty CHECK (token != '')
);

CREATE INDEX idx_sessoes_token ON sessoes(token);
CREATE INDEX idx_sessoes_usuario_id ON sessoes(usuario_id);
CREATE INDEX idx_sessoes_expirado_em ON sessoes(expirado_em);

-- Tabela de logs
CREATE TABLE registros_acesso (
  id SERIAL PRIMARY KEY,
  usuario_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
  tipo_evento VARCHAR(50),
  endereco_ip VARCHAR(50),
  sucesso BOOLEAN,
  mensagem VARCHAR(255),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_registros_usuario_id ON registros_acesso(usuario_id);
CREATE INDEX idx_registros_criado_em ON registros_acesso(criado_em);
CREATE INDEX idx_registros_tipo_evento ON registros_acesso(tipo_evento);

-- Usuário de teste (senha: 123456)
-- Hash gerado com bcrypt (10 rounds)
INSERT INTO usuarios (email, senha) VALUES 
('teste@email.com', '$2b$10$N9qo8uLOickgx2ZMRZoMye');

-- Verificar
SELECT * FROM usuarios;
```

---

## 🔍 Queries Úteis

### Buscar Usuário por Email

```sql
SELECT id, email, senha, criado_em 
FROM usuarios 
WHERE email = 'teste@email.com';
```

### Ver Sessões Ativas

```sql
SELECT 
    s.id,
    u.email,
    s.endereco_ip,
    s.criado_em,
    s.expirado_em,
    CASE 
        WHEN s.expirado_em > NOW() THEN 'ATIVA'
        ELSE 'EXPIRADA'
    END AS status
FROM sessoes s
JOIN usuarios u ON u.id = s.usuario_id
ORDER BY s.criado_em DESC;
```

### Limpar Sessões Expiradas

```sql
DELETE FROM sessoes 
WHERE expirado_em < NOW();
```

### Ver Logs de Acesso (últimos 50)

```sql
SELECT 
    ra.id,
    u.email AS usuario,
    ra.tipo_evento,
    ra.sucesso,
    ra.mensagem,
    ra.endereco_ip,
    ra.criado_em
FROM registros_acesso ra
LEFT JOIN usuarios u ON u.id = ra.usuario_id
ORDER BY ra.criado_em DESC
LIMIT 50;
```

### Tentativas de Login Falhadas (últimas 24h)

```sql
SELECT 
    COUNT(*) AS tentativas,
    endereco_ip,
    MAX(criado_em) AS ultima_tentativa
FROM registros_acesso
WHERE 
    tipo_evento = 'login' 
    AND sucesso = FALSE 
    AND criado_em > NOW() - INTERVAL '24 hours'
GROUP BY endereco_ip
HAVING COUNT(*) > 3
ORDER BY tentativas DESC;
```

### Usuários Mais Ativos

```sql
SELECT 
    u.email,
    COUNT(ra.id) AS total_acessos,
    MAX(ra.criado_em) AS ultimo_acesso
FROM usuarios u
JOIN registros_acesso ra ON ra.usuario_id = u.id
WHERE ra.sucesso = TRUE
GROUP BY u.id, u.email
ORDER BY total_acessos DESC;
```

---

## 🔧 Manutenção

### Backup

```bash
# Backup completo
pg_dump -U postgres login_system > backup_$(date +%Y%m%d).sql

# Backup apenas dados
pg_dump -U postgres --data-only login_system > backup_data.sql

# Backup apenas schema
pg_dump -U postgres --schema-only login_system > backup_schema.sql
```

### Restore

```bash
psql -U postgres login_system < backup.sql
```

### Limpeza Automática (Cron Job)

```sql
-- Deletar sessões expiradas há mais de 7 dias
DELETE FROM sessoes 
WHERE expirado_em < NOW() - INTERVAL '7 days';

-- Deletar logs antigos (mais de 90 dias)
DELETE FROM registros_acesso 
WHERE criado_em < NOW() - INTERVAL '90 days';
```

---

## 📊 Estatísticas

### Tamanho das Tabelas

```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Contagem de Registros

```sql
SELECT 
    'usuarios' AS tabela, COUNT(*) AS total FROM usuarios
UNION ALL
SELECT 'sessoes', COUNT(*) FROM sessoes
UNION ALL
SELECT 'registros_acesso', COUNT(*) FROM registros_acesso;
```

---

## ⚠️ Diferenças com Schema Antigo

| Coluna | Status | Motivo |
|--------|--------|--------|
| `usuarios.nome` | ❌ REMOVIDA | Não essencial |
| `usuarios.ativo` | ❌ REMOVIDA | Simplificação |
| `usuarios.atualizado_em` | ❌ REMOVIDA | Não usado |
| `usuarios.ultimo_acesso` | ❌ REMOVIDA | Logs suficientes |
| `registros_acesso.email` | ❌ REMOVIDA | Redundante (use usuario_id) |
| `sessoes.agente_usuario` | ❌ REMOVIDA | Opcional |

**Vantagens:**
- ✅ Menos complexidade
- ✅ Menor tamanho de banco
- ✅ Queries mais rápidas
- ✅ Menos erros de coluna não existente
- ✅ Mais fácil de manter

---

## 🔐 Segurança

### Senhas
- **SEMPRE** use bcrypt com 10+ rounds
- **NUNCA** armazene senhas em plaintext
- **NUNCA** retorne hash de senha nas APIs

### Tokens
- Tokens JWT expiram em 24h
- Armazene tokens no localStorage (frontend)
- Limpe tokens expirados regularmente

### IPs
- Registre IPs para auditoria
- Implemente rate limiting por IP
- Bloqueie IPs com muitas falhas

---

## 📞 Suporte

**Arquivo:** `banco_dados/SCHEMA.md`  
**Versão:** 2.0  
**Última atualização:** 21 de janeiro de 2026
