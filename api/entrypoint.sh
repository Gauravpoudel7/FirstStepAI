#!/usr/bin/env bash
# Container entrypoint: run migrations (Postgres prod), seed demo users if
# the users table is empty, then exec the API server. Demo seeding only runs
# when the users table is empty so production data is never overwritten.

set -euo pipefail

# Detect dialect. Migrations are Postgres-only; SQLite dev runs create_all
# at app startup instead.
DB_URL="${DATABASE_URL:-}"
if [[ "$DB_URL" == postgresql* || "$DB_URL" == postgres* ]]; then
    echo "[entrypoint] alembic upgrade head (postgres)..."
    alembic upgrade head
else
    echo "[entrypoint] non-postgres DB (${DB_URL:-sqlite}); skipping alembic, using create_all at startup"
fi

echo "[entrypoint] checking demo seed..."
USER_COUNT=$(python -c "
from app.db.session import SessionLocal
from app.models.user import User
db = SessionLocal()
print(db.query(User).count())
db.close()
")

if [ "$USER_COUNT" = "0" ]; then
    echo "[entrypoint] users table empty; seeding demo accounts..."
    if [ -f /srv/app/data/users.json ] || [ -f ./data/users.json ] || [ -f /data/users.json ]; then
        python -m scripts.seed_from_json || echo "[entrypoint] seed_from_json returned non-zero"
    else
        echo "[entrypoint] no data/users.json found; skipping"
    fi
else
    echo "[entrypoint] $USER_COUNT users present, skipping seed"
fi

echo "[entrypoint] starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips='*'