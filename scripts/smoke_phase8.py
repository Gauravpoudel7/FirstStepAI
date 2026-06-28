#!/usr/bin/env python3
"""Phase 8 smoke — verify deployment artifacts are syntactically correct
and self-consistent. Does NOT require Docker.

Checks:
  * deploy/docker-compose.yml is valid YAML with 4 services and 4 volumes.
  * api/Dockerfile references pyproject + app + scripts + data.
  * web/Dockerfile has build + runtime stages with nginx.
  * web/nginx.conf has /api/v1/chat/ with proxy_buffering off.
  * api/entrypoint.sh is executable and references alembic + uvicorn.
  * deploy/env/*.env files are present and reference correct service names.
"""
from __future__ import annotations
import os
import re
import sys
import pathlib
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
passed = failed = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global passed, failed
    if cond:
        print(f"  PASS {label}")
        passed += 1
    else:
        print(f"  FAIL {label} -- {detail}")
        failed += 1


def main() -> int:
    print("--- docker-compose.yml ---")
    compose_path = REPO / "deploy" / "docker-compose.yml"
    check("file exists", compose_path.exists(), str(compose_path))
    data = yaml.safe_load(compose_path.read_text())
    svcs = list((data or {}).get("services", {}).keys())
    vols = list((data or {}).get("volumes", {}).keys())
    check("has 4 services", len(svcs) == 4, str(svcs))
    for s in ("postgres", "redis", "api", "web"):
        check(f"service {s!r} present", s in svcs)
    check("has 4 volumes", len(vols) == 4, str(vols))
    for v in ("pg_data", "redis_data", "vectorstore_data", "uploads_data"):
        check(f"volume {v!r} present", v in vols)

    api_svc = (data or {})["services"].get("api", {})
    check("api depends_on postgres+redis", set(api_svc.get("depends_on", {}).keys()) >= {"postgres", "redis"})
    check("api uses env_file api.env", api_svc.get("env_file") == ["env/api.env"])
    check("api has healthcheck", "healthcheck" in api_svc)

    web_svc = (data or {})["services"].get("web", {})
    check("web depends_on api", "api" in web_svc.get("depends_on", {}))
    ports = web_svc.get("ports") or []
    ports_str = " ".join(ports)
    check("web exposes 8080 (with WEB_PORT default)", "8080" in ports_str and ":80" in ports_str)

    print("--- api/Dockerfile ---")
    api_dockerfile = (REPO / "api" / "Dockerfile").read_text()
    check("FROM python:3.12-slim", "FROM python:3.12-slim" in api_dockerfile)
    check("COPY app ./app", "COPY app ./app" in api_dockerfile)
    check("COPY scripts ./scripts", "COPY scripts ./scripts" in api_dockerfile)
    check("COPY data ./data", "COPY data ./data" in api_dockerfile)
    check("HEALTHCHECK /healthz", "/healthz" in api_dockerfile)
    check("ENTRYPOINT entrypoint.sh", "entrypoint.sh" in api_dockerfile)

    print("--- web/Dockerfile ---")
    web_dockerfile = (REPO / "web" / "Dockerfile").read_text()
    check("multi-stage build", web_dockerfile.count("FROM") >= 2, "expected 2+ FROM lines")
    check("FROM node:20-alpine", "FROM node:20-alpine" in web_dockerfile)
    check("FROM nginx:1.27-alpine", "FROM nginx:1.27-alpine" in web_dockerfile)
    check("COPY nginx.conf", "nginx.conf" in web_dockerfile)
    check("npm run build", "npm run build" in web_dockerfile)

    print("--- web/nginx.conf ---")
    nginx = (REPO / "web" / "nginx.conf").read_text()
    check("/api/v1/chat/ location present", "/api/v1/chat/" in nginx)
    check("proxy_buffering off", "proxy_buffering off" in nginx)
    check("proxy_read_timeout 300s", "proxy_read_timeout 300s" in nginx)
    check("X-Accel-Buffering no", "X-Accel-Buffering no" in nginx)
    check("upstream firststepai_api", "upstream firststepai_api" in nginx)
    check("upstream points to api:8000", "server api:8000" in nginx)
    check("SPA fallback try_files /index.html", "try_files $uri /index.html" in nginx)

    print("--- api/entrypoint.sh ---")
    ep = REPO / "api" / "entrypoint.sh"
    check("entrypoint exists", ep.exists(), str(ep))
    check("entrypoint is executable", os.access(ep, os.X_OK), "needs +x")
    body = ep.read_text() if ep.exists() else ""
    check("handles alembic", "alembic upgrade head" in body)
    check("skips alembic on sqlite", "skipping alembic" in body)
    check("exec uvicorn", "exec uvicorn" in body)
    check("seeds if users empty", "users table empty" in body or "users_table_empty" in body or "User).count()" in body)

    print("--- env files ---")
    for name in ("api.env", "api.env.example", "postgres.env", "postgres.env.example"):
        p = REPO / "deploy" / "env" / name
        check(f"{name} exists", p.exists(), str(p))
    api_env = (REPO / "deploy" / "env" / "api.env").read_text()
    check("api.env DATABASE_URL=postgres", "postgresql+psycopg://firststepai:firststepai@postgres:5432" in api_env)
    check("api.env REDIS_URL=redis", "redis://redis:6379/0" in api_env)
    check("api.env POLICIES_PDF=/seed/", "POLICIES_PDF=/seed/" in api_env)
    check("api.env COMPANY_NAME=Umbrella", "Umbrella Corporation" in api_env)
    pg_env = (REPO / "deploy" / "env" / "postgres.env").read_text()
    check("postgres.env POSTGRES_DB", "POSTGRES_DB=" in pg_env)

    print("--- deploy/README.md ---")
    readme = REPO / "deploy" / "README.md"
    check("README exists", readme.exists())
    if readme.exists():
        text = readme.read_text()
        check("README references docker compose", "docker compose" in text)
        check("README lists demo accounts", "demo@umbrella.corp" in text)
        check("README has production checklist", "Production checklist" in text)

    print()
    print(f"PASSED {passed} / FAILED {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())