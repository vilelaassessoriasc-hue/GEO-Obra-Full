# Prompt de Integração (Agente Técnico "Codex")

Você é um agente técnico sênior responsável por colocar o projeto **GEO-Obra-Backend** em produção.

## Objetivo
- Validar ambiente
- Conectar ao Supabase (Postgres + PostGIS)
- Rodar migrações Alembic
- Exportar OpenAPI e publicar artefatos
- Build & push da imagem Docker para GHCR
- Preparar execução com docker-compose em produção

## Instruções (passos detalhados)
1. **Clonar projeto** e verificar estrutura (`app/`, `alembic/`, `scripts/`, `requirements.txt`, `Dockerfile`, `docker-compose.prod.yml`).
2. **Configurar segredos** no repositório GitHub:
   - `DATABASE_URL` (pooler Supabase com `sslmode=require`)
   - (opcional) `SENTRY_DSN`
3. **Gerar `.env.prod`** local a partir do template e confirmar `JWT_SECRET` forte (>=32 chars).
4. **Rodar CI** (`.github/workflows/ci.yml`): instalar deps, rodar testes, exportar OpenAPI.
5. **Executar workflow `migrate.yml` (manual)** para `alembic upgrade head` usando `DATABASE_URL` do Supabase.
6. **Build & push de imagem** (`deploy.yml`) para `ghcr.io/<owner>/<repo>/geoobra-api:latest`.
7. **Produção**: usar `docker-compose.prod.yml` apontando `DATABASE_URL` correto; não subir serviço `db` se usar Supabase.
8. **Verificar saúde**: `GET /health` deve responder `200`.
9. **Exportar e anexar** `openapi_export/redoc.html` ao release.
10. **Checklist de LGPD e segurança**: revisar permissões de localização no app móvel, logs, retenção de dados.

## Critérios de aceite
- Migrações aplicadas sem erro
- `/health` responde `200`
- OpenAPI exportado e armazenado como artifact
- Imagem publicada em GHCR
- Documentação atualizada no README
