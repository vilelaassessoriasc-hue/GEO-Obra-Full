## Deploy rápido (GitHub)

1. Crie um repositório novo no GitHub e faça o push do projeto.
2. Em **Settings > Secrets and variables > Actions > New repository secret**, adicione:
   - `DATABASE_URL` (Supabase pooler com `sslmode=require`)
3. Confira os workflows em `.github/workflows/`:
   - `ci.yml` (testes + export OpenAPI)
   - `deploy.yml` (build & push imagem Docker para GHCR)
   - `migrate.yml` (rodar Alembic manualmente com Supabase)
4. Rode `migrate.yml` (Workflow Dispatch) para aplicar migrações.
5. Rode `deploy.yml` (push na main) para publicar a imagem.
6. Suba em produção com `docker-compose.prod.yml`.
