# 📚 Documentação - Banco de Dados (PostgreSQL)

Esta pasta contém tudo que você precisa para configurar o banco de dados PostgreSQL no EasyPanel.

## 📂 Arquivos

### 1. `schema.sql`
**O que é:** Script SQL que cria todas as tabelas necessárias
**Conteúdo:**
- Tabela `usuarios` - Armazena dados dos usuários
- Tabela `sessoes` - Armazena tokens e sessões ativas
- Tabela `logs_acesso` - Registra tentativas de login

**Como usar:**
- Copie o conteúdo
- Cole no pgAdmin do EasyPanel (Query Tool)
- Clique em executar

### 2. `README.md`
**O que é:** Guia completo de configuração PostgreSQL
**Inclui:**
- Passo-a-passo para criar banco no EasyPanel
- Instruções para executar o schema
- Descrição de cada tabela
- Variáveis de ambiente necessárias
- Exemplos de código Node.js/Express
- Operações comuns (queries úteis PostgreSQL)
- Dicas de segurança
- Diferenças PostgreSQL vs MySQL

### 3. `db-config.js`
**O que é:** Arquivo de configuração pronto para usar em Node.js com PostgreSQL
**Inclui:**
- Pool de conexões usando biblioteca `pg`
- Funções auxiliares (getUserByEmail, createSession, etc)
- Middleware de autenticação JWT
- Exemplos de rotas protegidas
- Graceful shutdown

## 🚀 Quick Start (PostgreSQL)

1. **Criar Banco no EasyPanel**
   - Tipo: PostgreSQL 14+
   - Nome: `login_system`
   - Usuário: `login_user`
   - Porta: 5432

2. **Executar Schema**
   - pgAdmin → Query Tool → cole schema.sql → executar

3. **Configurar Backend**
   - Copie `db-config.js` para seu backend
   - Instale dependências: `npm install pg bcrypt jsonwebtoken express`
   - Configure variáveis de ambiente

4. **Conectar Frontend**
   - Seu frontend React já está pronto
   - Aponta para a API que você criar com Node.js

## 📋 Checklist

- [ ] Banco de dados PostgreSQL criado no EasyPanel
- [ ] Schema SQL executado
- [ ] Tabelas criadas com sucesso
- [ ] Usuário de teste inserido
- [ ] Variáveis de ambiente configuradas
- [ ] Backend conectando ao banco com `pg`
- [ ] Rotas de login testadas
- [ ] Logs registrando corretamente
- [ ] SSL configurado em produção

## 🔗 Próximos Passos

1. Criar backend Node.js/Express com as rotas de login
2. Usar `db-config.js` como base
3. Implementar JWT para segurança
4. Conectar ao frontend React já pronto
5. Fazer deploy tudo junto no EasyPanel

## 📊 Configuração PostgreSQL vs MySQL

| Aspecto | PostgreSQL | MySQL |
|--------|-----------|-------|
| **Porta** | 5432 | 3306 |
| **Admin** | pgAdmin | phpMyAdmin |
| **Auto Increment** | SERIAL | AUTO_INCREMENT |
| **Driver Node** | `pg` | `mysql2` |
| **Parâmetros** | $1, $2, $3 | ?, ?, ? |

## 📞 Dúvidas Frequentes

**P: Onde coloco o schema.sql?**
R: No pgAdmin do seu banco no EasyPanel (Tools → Query Tool), ou use SSH/psql.

**P: Como conecto Node.js ao PostgreSQL?**
R: Use o arquivo `db-config.js` como exemplo. Instale `npm install pg`.

**P: Qual porta usar?**
R: PostgreSQL usa porta 5432 por padrão. EasyPanel fornecerá um host específico.

**P: Como gerar hash de senha?**
R: Use bcrypt: `npm install bcrypt` e `bcrypt.hash('senha', 10)`

**P: Posso usar MySQL ao invés de PostgreSQL?**
R: Sim, mas você precisará:
- Alterar sintaxe SQL em schema.sql
- Trocar `pg` por `mysql2/promise` em db-config.js
- Ajustar as queries (?, ?, ? ao invés de $1, $2, $3)

---

**Criado em:** 19 de janeiro de 2026
**Versão:** 1.0 (PostgreSQL) ✅
**Status:** Pronto para Produção
