# 🔧 Script de Diagnóstico - Backend

Use estes comandos para testar a conectividade e saúde do backend:

## 1️⃣ Testar Health (Deve estar online após redeploy)
```powershell
curl.exe -X GET https://login-backend.znh7ry.easypanel.host/health -H "Content-Type: application/json"
```

**Esperado:**
```json
{"status":"OK","timestamp":"2026-01-20T..."}
```

---

## 2️⃣ Testar Health DB
```powershell
curl.exe -X GET https://login-backend.znh7ry.easypanel.host/health/db -H "Content-Type: application/json"
```

**Esperado:**
```json
{"status":"OK","db":"AVAILABLE","usuarios_count":1}
```

---

## 3️⃣ Testar Login (Simular requisição POST)
```powershell
$body = @{
    email = "teste@email.com"
    senha = "123456"
} | ConvertTo-Json

curl.exe -X POST https://login-backend.znh7ry.easypanel.host/api/auth/login `
  -H "Content-Type: application/json" `
  -H "Origin: https://login-interface.znh7ry.easypanel.host" `
  -d $body
```

**Esperado:**
```json
{
  "sucesso": true,
  "mensagem": "Login realizado",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "usuario": {
    "id": 1,
    "email": "teste@email.com",
    "nome": "Usuário Teste"
  }
}
```

---

## 4️⃣ Testar CORS Preflight
```powershell
curl.exe -X OPTIONS https://login-backend.znh7ry.easypanel.host/api/auth/login `
  -H "Origin: https://login-interface.znh7ry.easypanel.host" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: Content-Type" `
  -v
```

**Esperado:**
- Status: 200
- Header: `Access-Control-Allow-Origin: https://login-interface.znh7ry.easypanel.host`

---

## 5️⃣ Verificar Logs do Backend no EasyPanel

1. Abra o EasyPanel → Serviço **login-backend**
2. Vá para a aba **Logs**
3. Procure por:
   - Erros de conexão com DB
   - Erro de JWT_SECRET faltando
   - Erros de importação de módulos

---

## 📋 Checklist de Diagnóstico

- [ ] Redeploy do backend concluído no EasyPanel?
- [ ] Health check retorna 200 OK?
- [ ] Health DB mostra usuarios_count >= 1?
- [ ] Preflight OPTIONS retorna 200 com headers CORS?
- [ ] POST /api/auth/login retorna token válido?
- [ ] Nenhum erro nos logs do backend?

---

## 🚨 Se ainda falhar

1. **Verificar variáveis de ambiente do backend:**
   - `DB_HOST=login_auth_db` ✅
   - `JWT_SECRET=seu_valor` ✅
   - `DB_PASSWORD=Senha123456` ✅

2. **Verificar se o banco está online:**
   - Tente acessar via psql

3. **Reiniciar o backend:**
   - No EasyPanel, clique em "Redeploy" novamente

4. **Compartilhe os logs do backend** (últimas 30 linhas) para diagnóstico

---
