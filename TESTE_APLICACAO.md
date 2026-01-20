# 🧪 Plano de Teste - Aplicação de Login

## Data: 20 de janeiro de 2026

---

## ✅ Testes Realizados Localmente

### 1. Frontend Build
**Status:** ✅ **PASSOU**
```
vite v7.3.1 building for production...
✓ 95 modules transformed
✓ dist/index.html                   0.46 kB | gzip:  0.29 kB
✓ dist/assets/index-ByyqtS7W.css    3.69 kB | gzip:  1.03 kB
✓ dist/assets/index-CxtqRSZN.js   267.38 kB | gzip: 88.40 kB
```

**O que foi validado:**
- ✅ React + TypeScript compila sem erros
- ✅ Vite build otimizado para produção
- ✅ Tamanho de bundle OK (~88KB gzip)

---

## 🧪 Testes a Executar no EasyPanel

### 2. Backend - Health Check
```bash
curl https://login-backend.znh7ry.easypanel.host/health
```
**Esperado:**
```json
{"status":"OK","timestamp":"2026-01-20T..."}
```

### 3. Backend - Database Health Check
```bash
curl https://login-backend.znh7ry.easypanel.host/health/db
```
**Esperado:**
```json
{"status":"OK","db":"AVAILABLE","usuarios_count":1}
```

---

### 4. Teste de Login (Manual)

**Pré-requisitos:**
- Backend redeployado com as correções mais recentes
- Banco de dados com tabelas criadas
- Usuário de teste: `teste@email.com` com senha `123456`

**Passos:**
1. Abrir https://login-interface.znh7ry.easypanel.host
2. Preencher formulário:
   - Email: `teste@email.com`
   - Senha: `123456`
3. Clicar em "ENTRAR"

**Esperado:**
- ✅ Requisição POST para `/api/auth/login` com status 200
- ✅ Resposta contém `token`, `usuario.id`, `usuario.email`, `usuario.nome`
- ✅ Token armazenado no localStorage
- ✅ Redirecionamento para `/success`
- ✅ Página de sucesso exibe email e nome do usuário

**Se falhar:**
- Verificar console do navegador (F12 → Console) para erros
- Verificar logs do backend no EasyPanel
- Confirmar CORS está permitindo a origem

---

### 5. Teste de JWT - Verificar Token
```bash
curl -X POST https://login-backend.znh7ry.easypanel.host/api/auth/verify \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Esperado:**
```json
{"sucesso":true,"mensagem":"Token valido","usuario":{...}}
```

---

## 🔍 Validações de Código

### Backend (app.py)
- ✅ CORS configurado para frontend domain
- ✅ Suporta senha plaintext E bcrypt
- ✅ Validação de JWT_SECRET obrigatória
- ✅ Fallback para nome NULL
- ✅ Endpoints: `/health`, `/health/db`, `/api/auth/login`, `/api/auth/verify`

### Frontend (Login.tsx, api.ts)
- ✅ Requisição POST com email e senha
- ✅ Armazena token no localStorage
- ✅ Navega para `/success` após login
- ✅ Exibe erros em caso de falha
- ✅ Loading state durante requisição

### Banco de Dados
- ✅ Tabela `usuarios` com columns: id, email, senha, nome, ativo, criado_em
- ✅ Tabela `sessoes` com columns: id, usuario_id, token, expirado_em
- ✅ Tabela `registros_acesso` para auditoria
- ✅ Usuário teste inserido: `teste@email.com`

---

## 📋 Checklist Final

- [ ] Backend redeployado com commits:
  - `d822919` - Suporta senha plaintext e bcrypt
  - `2f78d61` - Validar JWT_SECRET + fallback nome
  
- [ ] Frontend redeployado (último push em main)

- [ ] Testes de saúde passando:
  - [ ] GET /health → 200 OK
  - [ ] GET /health/db → 200 OK + usuarios_count

- [ ] Teste de login funcionando:
  - [ ] Email/senha aceitos
  - [ ] Token gerado e armazenado
  - [ ] Redirecionamento para success page
  - [ ] Sem erros de CORS

- [ ] Sem erros de JavaScript no console

---

## 🚀 Conclusão

**Status Geral:** Pronto para teste de produção

**Próximas ações:**
1. Reimplantar backend com commits d822919 e 2f78d61
2. Executar testes de saúde
3. Testar login de ponta a ponta
4. Se tudo OK → Sistema em produção ✅

---
