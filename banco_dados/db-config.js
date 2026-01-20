// =====================================================
// Exemplo de Configuração do Banco de Dados
// Para Node.js + Express Backend com PostgreSQL
// =====================================================

const { Pool, Client } = require('pg');

// =====================================================
// Pool de Conexões PostgreSQL
// =====================================================
const pool = new Pool({
  // Conexão
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  user: process.env.DB_USER || 'login_user',
  password: process.env.DB_PASSWORD || 'senha123',
  database: process.env.DB_DATABASE || 'login_system',
  
  // Pool Settings
  max: parseInt(process.env.DB_POOL_LIMIT || 10),
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  
  // SSL (recomendado em produção)
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// Event listeners
pool.on('error', (err) => {
  console.error('Erro inesperado no pool:', err);
});

// =====================================================
// Funções de Ajuda
// =====================================================

/**
 * Buscar usuário por email
 */
async function getUserByEmail(email) {
  const result = await pool.query(
    'SELECT * FROM usuarios WHERE email = $1 AND ativo = TRUE',
    [email]
  );
  return result.rows[0] || null;
}

/**
 * Buscar usuário por ID
 */
async function getUserById(userId) {
  const result = await pool.query(
    'SELECT id, email, nome, criado_em, ultimo_acesso FROM usuarios WHERE id = $1 AND ativo = TRUE',
    [userId]
  );
  return result.rows[0] || null;
}

/**
 * Criar nova sessão
 */
async function createSession(userId, token, ipAddress, userAgent) {
  const expiradoEm = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 horas
  
  const result = await pool.query(
    'INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, expirado_em) VALUES ($1, $2, $3, $4, $5) RETURNING id',
    [userId, token, ipAddress, userAgent, expiradoEm]
  );
  
  return result.rows[0].id;
}

/**
 * Validar token
 */
async function validateToken(token) {
  const result = await pool.query(
    `SELECT u.* FROM usuarios u 
     INNER JOIN sessoes s ON u.id = s.usuario_id 
     WHERE s.token = $1 AND s.expirado_em > NOW() AND u.ativo = TRUE`,
    [token]
  );
  
  return result.rows[0] || null;
}

/**
 * Fazer logout (deletar sessão)
 */
async function deleteSession(token) {
  const result = await pool.query(
    'DELETE FROM sessoes WHERE token = $1',
    [token]
  );
  
  return result.rowCount > 0;
}

/**
 * Registrar log de acesso
 */
async function logAccess(userId, email, tipoEvento, ipAddress, sucesso, mensagem = '') {
  await pool.query(
    'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso, mensagem) VALUES ($1, $2, $3, $4, $5, $6)',
    [userId || null, email, tipoEvento, ipAddress, sucesso, mensagem]
  );
}

/**
 * Atualizar último acesso
 */
async function updateLastAccess(userId) {
  await pool.query(
    'UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = $1',
    [userId]
  );
}

/**
 * Deletar sessões expiradas
 */
async function cleanExpiredSessions() {
  const result = await pool.query(
    'DELETE FROM sessoes WHERE expirado_em < NOW()'
  );
  
  return result.rowCount;
}

// =====================================================
// Middleware de Autenticação
// =====================================================

async function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    return res.status(401).json({ error: 'Token não fornecido' });
  }
  
  try {
    const user = await validateToken(token);
    
    if (!user) {
      return res.status(403).json({ error: 'Token inválido ou expirado' });
    }
    
    req.user = user;
    next();
  } catch (error) {
    console.error('Erro ao validar token:', error);
    res.status(500).json({ error: 'Erro ao validar token' });
  }
}

// =====================================================
// Exemplo de Rota de Login
// =====================================================

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

app.post('/login', async (req, res) => {
  const { email, senha } = req.body;
  const ipAddress = req.ip;
  const userAgent = req.get('user-agent');
  
  try {
    // Validar entrada
    if (!email || !senha) {
      await logAccess(null, email || 'unknown', 'login', ipAddress, false, 'Email ou senha vazio');
      return res.status(400).json({ error: 'Email e senha são obrigatórios' });
    }
    
    // Buscar usuário
    const user = await getUserByEmail(email);
    
    if (!user) {
      await logAccess(null, email, 'login', ipAddress, false, 'Usuário não encontrado');
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Validar senha (bcrypt)
    const senhaValida = await bcrypt.compare(senha, user.senha);
    
    if (!senhaValida) {
      await logAccess(user.id, email, 'login', ipAddress, false, 'Senha incorreta');
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Gerar JWT
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET || 'sua-chave-secreta',
      { expiresIn: process.env.JWT_EXPIRY || '24h' }
    );
    
    // Criar sessão
    await createSession(user.id, token, ipAddress, userAgent);
    
    // Log de sucesso
    await logAccess(user.id, email, 'login', ipAddress, true, 'Login bem-sucedido');
    
    // Atualizar último acesso
    await updateLastAccess(user.id);
    
    // Responder
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        nome: user.nome
      }
    });
    
  } catch (error) {
    console.error('Erro ao fazer login:', error);
    await logAccess(null, email, 'login', ipAddress, false, error.message);
    res.status(500).json({ error: 'Erro ao fazer login' });
  }
});

// =====================================================
// Exemplo de Rota Protegida
// =====================================================

app.get('/perfil', authenticateToken, async (req, res) => {
  try {
    const user = await getUserById(req.user.id);
    res.json(user);
  } catch (error) {
    console.error('Erro ao buscar perfil:', error);
    res.status(500).json({ error: 'Erro ao buscar perfil' });
  }
});

// =====================================================
// Cleanup de Sessões Expiradas (Cron Job)
// =====================================================

// Executar a cada hora
setInterval(async () => {
  try {
    const deleted = await cleanExpiredSessions();
    console.log(`✅ ${deleted} sessões expiradas deletadas`);
  } catch (error) {
    console.error('Erro ao limpar sessões:', error);
  }
}, 60 * 60 * 1000); // 1 hora

// =====================================================
// Graceful Shutdown
// =====================================================

process.on('SIGINT', async () => {
  console.log('Encerrando aplicação...');
  await pool.end();
  process.exit(0);
});

// =====================================================
// Exportar
// =====================================================

module.exports = {
  pool,
  getUserByEmail,
  getUserById,
  createSession,
  validateToken,
  deleteSession,
  logAccess,
  updateLastAccess,
  cleanExpiredSessions,
  authenticateToken,
};

// =====================================================
// Funções de Ajuda
// =====================================================

/**
 * Buscar usuário por email
 */
async function getUserByEmail(email) {
  const [users] = await pool.query(
    'SELECT * FROM usuarios WHERE email = ? AND ativo = TRUE',
    [email]
  );
  return users[0] || null;
}

/**
 * Buscar usuário por ID
 */
async function getUserById(userId) {
  const [users] = await pool.query(
    'SELECT id, email, nome, criado_em, ultimo_acesso FROM usuarios WHERE id = ? AND ativo = TRUE',
    [userId]
  );
  return users[0] || null;
}

/**
 * Criar nova sessão
 */
async function createSession(userId, token, ipAddress, userAgent) {
  const expiradoEm = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 horas
  
  const [result] = await pool.query(
    'INSERT INTO sessoes (usuario_id, token, ip_address, user_agent, expirado_em) VALUES (?, ?, ?, ?, ?)',
    [userId, token, ipAddress, userAgent, expiradoEm]
  );
  
  return result.insertId;
}

/**
 * Validar token
 */
async function validateToken(token) {
  const [sessions] = await pool.query(
    `SELECT u.* FROM usuarios u 
     INNER JOIN sessoes s ON u.id = s.usuario_id 
     WHERE s.token = ? AND s.expirado_em > NOW() AND u.ativo = TRUE`,
    [token]
  );
  
  return sessions[0] || null;
}

/**
 * Fazer logout (deletar sessão)
 */
async function deleteSession(token) {
  const [result] = await pool.query(
    'DELETE FROM sessoes WHERE token = ?',
    [token]
  );
  
  return result.affectedRows > 0;
}

/**
 * Registrar log de acesso
 */
async function logAccess(userId, email, tipoEvento, ipAddress, sucesso, mensagem = '') {
  await pool.query(
    'INSERT INTO logs_acesso (usuario_id, email, tipo_evento, ip_address, sucesso, mensagem) VALUES (?, ?, ?, ?, ?, ?)',
    [userId || null, email, tipoEvento, ipAddress, sucesso, mensagem]
  );
}

/**
 * Atualizar último acesso
 */
async function updateLastAccess(userId) {
  await pool.query(
    'UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = ?',
    [userId]
  );
}

/**
 * Deletar sessões expiradas
 */
async function cleanExpiredSessions() {
  const [result] = await pool.query(
    'DELETE FROM sessoes WHERE expirado_em < NOW()'
  );
  
  return result.affectedRows;
}

// =====================================================
// Middleware de Autenticação
// =====================================================

async function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token) {
    return res.status(401).json({ error: 'Token não fornecido' });
  }
  
  try {
    const user = await validateToken(token);
    
    if (!user) {
      return res.status(403).json({ error: 'Token inválido ou expirado' });
    }
    
    req.user = user;
    next();
  } catch (error) {
    console.error('Erro ao validar token:', error);
    res.status(500).json({ error: 'Erro ao validar token' });
  }
}

// =====================================================
// Exemplo de Rota de Login
// =====================================================

const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

app.post('/login', async (req, res) => {
  const { email, senha } = req.body;
  const ipAddress = req.ip;
  const userAgent = req.get('user-agent');
  
  try {
    // Validar entrada
    if (!email || !senha) {
      await logAccess(null, email || 'unknown', 'login', ipAddress, false, 'Email ou senha vazio');
      return res.status(400).json({ error: 'Email e senha são obrigatórios' });
    }
    
    // Buscar usuário
    const user = await getUserByEmail(email);
    
    if (!user) {
      await logAccess(null, email, 'login', ipAddress, false, 'Usuário não encontrado');
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Validar senha (bcrypt)
    const senhaValida = await bcrypt.compare(senha, user.senha);
    
    if (!senhaValida) {
      await logAccess(user.id, email, 'login', ipAddress, false, 'Senha incorreta');
      return res.status(401).json({ error: 'Email ou senha inválidos' });
    }
    
    // Gerar JWT
    const token = jwt.sign(
      { id: user.id, email: user.email },
      process.env.JWT_SECRET || 'sua-chave-secreta',
      { expiresIn: process.env.JWT_EXPIRY || '24h' }
    );
    
    // Criar sessão
    await createSession(user.id, token, ipAddress, userAgent);
    
    // Log de sucesso
    await logAccess(user.id, email, 'login', ipAddress, true, 'Login bem-sucedido');
    
    // Atualizar último acesso
    await updateLastAccess(user.id);
    
    // Responder
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email,
        nome: user.nome
      }
    });
    
  } catch (error) {
    console.error('Erro ao fazer login:', error);
    await logAccess(null, email, 'login', ipAddress, false, error.message);
    res.status(500).json({ error: 'Erro ao fazer login' });
  }
});

// =====================================================
// Exemplo de Rota Protegida
// =====================================================

app.get('/perfil', authenticateToken, async (req, res) => {
  try {
    const user = await getUserById(req.user.id);
    res.json(user);
  } catch (error) {
    console.error('Erro ao buscar perfil:', error);
    res.status(500).json({ error: 'Erro ao buscar perfil' });
  }
});

// =====================================================
// Cleanup de Sessões Expiradas (Cron Job)
// =====================================================

// Executar a cada hora
setInterval(async () => {
  try {
    const deleted = await cleanExpiredSessions();
    console.log(`✅ ${deleted} sessões expiradas deletadas`);
  } catch (error) {
    console.error('Erro ao limpar sessões:', error);
  }
}, 60 * 60 * 1000); // 1 hora

// =====================================================
// Exportar
// =====================================================

module.exports = {
  pool,
  getUserByEmail,
  getUserById,
  createSession,
  validateToken,
  deleteSession,
  logAccess,
  updateLastAccess,
  cleanExpiredSessions,
  authenticateToken,
};
