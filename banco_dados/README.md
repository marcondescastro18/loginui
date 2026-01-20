# 🗄️ Banco de Dados - Login System (PostgreSQL)

Documentação completa do banco de dados PostgreSQL no EasyPanel.

## 📋 Configuração Atual

| Item | Valor |
|------|-------|
| **Host Interno** | `login_login-aut-db` |
| **Porta** | `5432` |
| **Usuário** | `postgres` |
| **Senha** | `fa0e7201e1773b163eb3` |
| **Database** | `auth_db` |
| **Versão** | PostgreSQL 17.7 |

## 📊 Tabelas

### `usuarios`
- id (SERIAL PRIMARY KEY)
- email (VARCHAR UNIQUE)
- senha (VARCHAR) - Hash bcrypt
- nome (VARCHAR)
- ativo (BOOLEAN)
- criado_em, atualizado_em, ultimo_acesso (TIMESTAMP)

### `sessoes`
- id (SERIAL PRIMARY KEY)
- usuario_id (FK)
- token (VARCHAR UNIQUE)
- endereco_ip, agente_usuario
- expirado_em, criado_em

### `registros_acesso`
- id (SERIAL PRIMARY KEY)
- usuario_id (FK nullable)
- email, tipo_evento, endereco_ip
- sucesso (BOOLEAN)
- mensagem, criado_em

## 🔧 Scripts Disponíveis

Execute no **Terminal do Backend (EasyPanel)**:

```bash
# Listar todas as tabelas e dados
python list_database.py

# Criar novo usuário com bcrypt
python create_user.py

# Atualizar teste@email.com para bcrypt
python update_test_user.py
```

## 🔍 Queries Úteis

```sql
-- Ver usuários
SELECT id, email, nome, ativo FROM usuarios;

-- Ver tipo de senha
SELECT email, 
  CASE WHEN senha LIKE '$2%' THEN 'bcrypt' ELSE 'plaintext' END as tipo
FROM usuarios;

-- Logs de login
SELECT u.email, r.sucesso, r.mensagem, r.criado_em
FROM registros_acesso r
LEFT JOIN usuarios u ON r.usuario_id = u.id
ORDER BY r.criado_em DESC
LIMIT 10;
```

## 🔐 Segurança

- ✅ Senhas com bcrypt (nunca plaintext em produção)
- ✅ JWT_SECRET obrigatório no backend
- ✅ Queries com parâmetros (proteção SQL injection)
- ✅ HTTPS automático via EasyPanel

## 📚 Documentação Completa

Veja `backend/AUTH_README.md` para detalhes sobre autenticação.

---

**Versão:** 2.0  
**Data:** 20/01/2026  
**Status:** ✅ Produção
