# 🚀 Guia de Deploy - EasyPanel

## ✅ Pré-requisitos Atendidos
- [x] Vite + React + TypeScript
- [x] Build otimizado
- [x] Scripts corretos
- [x] Dependências instaladas
- [x] Interface moderna

## 📋 Checklist de Deploy

### 1️⃣ Antes do Push
```bash
# Teste a build localmente
npm run build

# Teste o servidor de preview
npm run start
```

### 2️⃣ Configurar Repositório Git
```bash
# Inicializar git (se não estiver)
git init
git add .
git commit -m "Initial commit: Login UI Vite+React"
git branch -M main
git remote add origin https://seu-repo.git
git push -u origin main
```

### 3️⃣ Configurar EasyPanel

**Passo 1: Criar aplicação Node.js**
- Nome: `login-ui`
- Versão Node: `18` ou superior
- Ambiente: Produção

**Passo 2: Conectar repositório**
- GitHub/GitLab/Gitea (seu repositório)
- Branch: `main`
- Auto-deploy: ✅ Ativado

**Passo 3: Configurar Build**
```
Build Command: npm install && npm run build
Start Command: npm run start
Port: 3000
```

**Passo 4: Variáveis de Ambiente**
```
NODE_ENV=production
```

### 4️⃣ Domínio (Opcional)
- Domínio: seu-dominio.com
- SSL: ✅ Automático (Let's Encrypt)

## 🔗 API do Login
**URL da API:** `https://login-servico.znh7ry.easypanel.host`
- Endpoint: `/login`
- Método: `POST`
- Body: `{ "email": "user@email.com", "senha": "password" }`
- Response: `{ "token": "seu_token" }`

## 📝 Estrutura Final
```
login-ui/
├── src/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Login.css
│   │   ├── Success.tsx
│   │   └── Success.css
│   ├── services/
│   │   └── api.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── dist/ (gerado ao fazer build)
├── package.json
├── vite.config.ts
├── tsconfig.json
└── index.html
```

## ✨ Recursos Implementados
- ✅ Login com validação
- ✅ Armazenamento de token (localStorage)
- ✅ Navegação entre páginas
- ✅ Interface moderna e responsiva
- ✅ Tratamento de erros
- ✅ Loading states
- ✅ Logout

## 🛠️ Troubleshooting

**Erro: "Cannot find module"**
- Limpar cache: `rm -rf node_modules/.vite`
- Reinstalar: `npm install`

**Build falha**
- Verificar: `npm run build` localmente
- Verificar Node.js: `node --version` (deve ser 16+)

**Porta 3000 em uso**
- Mudar porta em `vite.config.ts`
- Ou usar variável de ambiente

## 🎯 Próximos Passos
1. Fazer commit e push para git
2. Criar conta no EasyPanel
3. Conectar repositório
4. Configurar conforme guia acima
5. Fazer deploy
6. Testar em produção

---
**Pronto para produção! 🎉**
