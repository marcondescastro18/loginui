-- =====================================================
-- Login System Database Schema
-- PostgreSQL Version
-- =====================================================

-- Criar banco de dados (se não existir)
-- PostgreSQL
-- CREATE DATABASE login_system;
-- \c login_system

-- Criar extensões (se necessário)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- Tabela de Usuários
-- =====================================================
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

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_ativo ON usuarios(ativo);

-- =====================================================
-- Tabela de Sessões/Tokens
-- =====================================================
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

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_sessoes_token ON sessoes(token);
CREATE INDEX IF NOT EXISTS idx_sessoes_usuario_id ON sessoes(usuario_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_expirado_em ON sessoes(expirado_em);
CREATE INDEX IF NOT EXISTS idx_sessoes_endereco_ip ON sessoes(endereco_ip);

-- =====================================================
-- Tabela de Logs de Acesso
-- =====================================================
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

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_registros_usuario_id ON registros_acesso(usuario_id);
CREATE INDEX IF NOT EXISTS idx_registros_criado_em ON registros_acesso(criado_em);
CREATE INDEX IF NOT EXISTS idx_registros_tipo_evento ON registros_acesso(tipo_evento);
CREATE INDEX IF NOT EXISTS idx_registros_endereco_ip ON registros_acesso(endereco_ip);

-- =====================================================
-- Inserir Usuário de Teste
-- =====================================================
-- Senha: 123456 (NÃO usar em produção!)
-- Para gerar hash em produção, usar bcrypt
-- Hash exemplo: $2b$10$YourBcryptHashHere

INSERT INTO usuarios (email, nome, senha) VALUES 
('teste@email.com', 'Usuário Teste', '$2b$10$N9qo8uLOickgx2ZMRZoMye');

-- =====================================================
-- Exemplos de Queries Úteis (PostgreSQL)
-- =====================================================

-- Buscar usuário por email
-- SELECT * FROM usuarios WHERE email = 'teste@email.com' AND ativo = TRUE;

-- Criar sessão após login
-- INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) 
-- VALUES (1, 'token_jwt_aqui', '192.168.1.1', NOW() + INTERVAL '24 hours');

-- Validar token
-- SELECT u.* FROM usuarios u 
-- INNER JOIN sessoes s ON u.id = s.usuario_id 
-- WHERE s.token = 'token_aqui' AND s.expirado_em > NOW();

-- Registro de acesso
-- INSERT INTO registros_acesso (usuario_id, email, tipo_evento, endereco_ip, sucesso) 
-- VALUES (1, 'teste@email.com', 'login', '192.168.1.1', TRUE);

-- =====================================================
-- Relatórios (PostgreSQL)
-- =====================================================

-- Usuários mais ativos
-- SELECT email, COUNT(*) as acessos 
-- FROM registros_acesso 
-- WHERE tipo_evento = 'login' 
-- GROUP BY usuario_id, email
-- ORDER BY acessos DESC;

-- Tentativas falhadas de login (últimas 24h)
-- SELECT email, COUNT(*) as tentativas 
-- FROM registros_acesso 
-- WHERE tipo_evento = 'login' AND sucesso = FALSE AND criado_em > NOW() - INTERVAL '24 hours' 
-- GROUP BY email 
-- HAVING COUNT(*) > 3;
