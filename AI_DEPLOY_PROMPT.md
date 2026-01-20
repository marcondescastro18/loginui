# Prompt de IA – Deploy React (Vite) + Flask + PostgreSQL no EasyPanel

Use este prompt em um agente de IA (Copilot/ChatGPT) para automatizar a preparação e o deploy do stack. Substitua os placeholders entre <...> antes de usar.

---

## Contexto
- Monorepo com:
  - Frontend: Vite + React + TypeScript (porta 3000 via `vite preview`)
  - Backend: Python Flask + gunicorn (porta 3000)
  - Banco: PostgreSQL
- Deploy alvo: EasyPanel com Nixpacks

## Objetivo
- Construir e implantar backend e frontend no EasyPanel, com PostgreSQL, domínios públicos e comunicação segura entre os serviços.
- Garantir testes de saúde (`/health`) e login de ponta a ponta.

## Variáveis (preencha antes de rodar)
- GitHub
  - OWNER = <github_owner>
  - REPO = <github_repo>
  - BRANCH = main
- EasyPanel – Serviços
  - POSTGRES_SERVICE = <nome_do_servico_do_postgres>
  - BACKEND_SERVICE = <nome_do_servico_backend>  (ex.: login-api)
  - FRONTEND_SERVICE = <nome_do_servico_frontend> (ex.: loginui ou interface)
- Domínios (públicos gerados pelo EasyPanel)
  - BACKEND_DOMAIN = <https://seu-backend.easypanel.host>
  - FRONTEND_DOMAIN = <https://seu-frontend.easypanel.host>
- Banco
  - DB_HOST = postgres  (nome do serviço interno do banco)
  - DB_PORT = 5432
  - DB_USER = auth_db
  - DB_PASSWORD = <senha_segura>
  - DB_NAME = auth_db
- App
  - JWT_SECRET = <chave_jwt_segura>
  - NODE_VERSION = 20.19.0

## Regras e Restrições
- Nunca use `localhost` ou `127.0.0.1` entre serviços no EasyPanel.
- Backend deve escutar em 0.0.0.0:3000 (gunicorn). Procfile: `web: gunicorn -b 0.0.0.0:${PORT:-3000} app:app`.
- Frontend deve publicar via `vite preview --host 0.0.0.0 --port 3000 --strictPort`.
- `VITE_API_URL` deve apontar para BACKEND_DOMAIN (público).
- `vite.config.ts` precisa incluir `preview.allowedHosts` com FRONTEND_DOMAIN (sem protocolo).
- Node para o frontend: `NODE_VERSION>=20.19`.
- Mapear Domínios no EasyPanel: HTTPS público → Destino HTTP porta 3000 caminho `/`.

## Plano de Ação (o que a IA deve fazer)
1) Verificar repo
   - Confirmar presença de: `backend/requirements.txt`, `backend/Procfile`, `backend/app.py`, `vite.config.ts`, `package.json`, `src/services/api.ts`.
   - Checar se `api.ts` usa `import.meta.env.VITE_API_URL` como baseURL.
2) Backend – dependências e execução
   - Garantir em `requirements.txt`: Flask, Flask-CORS, psycopg2-binary, PyJWT (2.10.1), bcrypt, python-dotenv, gunicorn (21.x).
   - Confirmar `Procfile` conforme regra.
3) PostgreSQL
   - Criar serviço POSTGRES no EasyPanel.
   - Executar `banco_dados/schema.sql` (copiar conteúdo e rodar no console SQL).
4) Backend – criar serviço App
   - Source: GitHub (OWNER/REPO/BRANCH), Build: Nixpacks, Build Path: `backend`.
   - Variáveis de ambiente:
     ```
     DB_HOST=postgres
     DB_PORT=5432
     DB_USER=auth_db
     DB_PASSWORD=<senha_segura>
     DB_NAME=auth_db
     JWT_SECRET=<chave_jwt_segura>
     PORT=3000
     ```
   - Domínios: BACKEND_DOMAIN → Destino HTTP 3000 `/` (HTTPS ligado).
   - Implantar e validar `GET BACKEND_DOMAIN/health` == 200.
5) Frontend – ajustes de código
   - Em `vite.config.ts`, adicionar:
     ```ts
     preview: { host: '0.0.0.0', port: 3000, strictPort: true, allowedHosts: ['<frente.sem.protocolo>'] }
     ```
   - Em `src/services/api.ts`: `baseURL` usar `import.meta.env.VITE_API_URL` e fallback BACKEND_DOMAIN.
6) Frontend – criar serviço App
   - Source: GitHub (OWNER/REPO/BRANCH), Build: Nixpacks, Build Path: `/`.
   - Comandos (opcional): Build `npm run build`, Start `npm run start`.
   - Variáveis de ambiente:
     ```
     VITE_API_URL=<BACKEND_DOMAIN>
     NODE_VERSION=20.19.0
     ```
   - Domínios: FRONTEND_DOMAIN → Destino HTTP 3000 `/` (HTTPS ligado).
   - Implantar.
7) Smoke Tests
   - Acessar FRONTEND_DOMAIN (carregar sem 502/host bloqueado).
   - Chamar `BACKEND_DOMAIN/health` (200 OK).
   - Tentar login com usuário de teste do schema (senha 123456) e validar redirecionamento.
8) Saídas Esperadas (entregar)
   - URLs finais: BACKEND_DOMAIN, FRONTEND_DOMAIN.
   - Status checks: `/health` 200, print do console do navegador sem 502, e resposta de `/api/auth/login`.
   - Lista de variáveis de ambiente usadas no EasyPanel.

## Critérios de Aceite
- Backend acessível publicamente via `/health`.
- Frontend acessível publicamente, sem erro de host bloqueado.
- Login funcionando usando o usuário seed do banco.
- Toda configuração documentada e reprodutível.

## Observações
- Caso o EasyPanel use nomes de serviço diferentes, atualizar `DB_HOST` para o nome interno do Postgres.
- Em caso de erro 502 no frontend, verificar: porta destino (3000), `NODE_VERSION`, `allowedHosts` e reimplantar.
