# FirstStep AI — Production Deployment

Single-command stack: PostgreSQL + Redis + FastAPI + React/nginx.

```bash
cp deploy/env/api.env.example deploy/env/api.env
cp deploy/env/postgres.env.example deploy/env/postgres.env
# Edit api.env: set AUTH_SECRET and (optionally) GROQ_API_KEY.
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml ps   # all "healthy"
```

Then open <http://localhost:8080>. The bundled demo accounts
(`admin@`, `hr@`, `manager@`, `employee@`, `demo@umbrella.corp` — all
`demo123`) are seeded automatically on first run.

## Services

| Service | Image | Port (host) | Healthcheck |
|---|---|---|---|
| `web`   | build from `web/Dockerfile` (nginx:1.27-alpine) | 8080 | `wget /` |
| `api`   | build from `api/Dockerfile` (python:3.12-slim) | 8000 (internal) | `curl /healthz` |
| `postgres` | postgres:16-alpine | 5432 | `pg_isready` |
| `redis`    | redis:7-alpine      | 6379 | `redis-cli ping` |

## Volumes

| Volume | Mounted at | Purpose |
|---|---|---|
| `pg_data` | `/var/lib/postgresql/data` | Postgres persistence |
| `redis_data` | `/data` | AOF persistence |
| `vectorstore_data` | `/data/vectorstore` | Chroma index (writable) |
| `uploads_data` | `/data/uploads` | Future: admin-uploaded files |

The bundled Chroma index + PDF are bind-mounted **read-only** at `/seed/`
inside the api container; the api's lifespan startup copies them into
`/data/vectorstore` if the index is missing.

## SSE streaming

`web/nginx.conf` has two `/api/v1/chat/` location blocks with
`proxy_buffering off`, `proxy_read_timeout 300s`, and the
`X-Accel-Buffering: no` header so tokens stream end-to-end.

## Smoke tests

```bash
# Backend (assumes stack is up at http://localhost:8080)
python scripts/smoke_phase1_http.py
python scripts/smoke_phase3_http.py
python scripts/smoke_phase4.py
python scripts/smoke_phase5.py
python scripts/smoke_phase6.py
python scripts/smoke_phase7.py

# Frontend (Playwright contract test)
cd web && npm install && npx playwright install --with-deps chromium
E2E_BASE_URL=http://localhost:8080 npm run test:e2e
```

## Production checklist

Before going live:

- [ ] Set `AUTH_SECRET` to a 32+ byte random value in `deploy/env/api.env`.
- [ ] Set `GROQ_API_KEY` (or change `LLM_PROVIDER` to `mock` for offline).
- [ ] Set `COOKIE_SECURE=true` and configure `COOKIE_DOMAIN` for HTTPS.
- [ ] Restrict `CORS_ORIGINS` to your real domain.
- [ ] Replace the bundled Chroma index with a fresh re-index (`POST /api/v1/documents/reindex`).
- [ ] Point nginx at a real TLS cert (replace the dev config with the production `default.conf`).
- [ ] Back up `pg_data`, `vectorstore_data`, and `uploads_data` volumes.