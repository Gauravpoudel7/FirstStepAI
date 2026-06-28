# FirstStep AI — API (FastAPI + LangChain + Groq + Chroma)
# Multi-stage keeps the runtime slim and reproducible.
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps: libpq for psycopg, build tools for bcrypt + chromadb wheels, curl for healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app

# Install Python deps first so layer cache survives code edits.
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install .

# Copy application code (alembic lives under app/, scripts at root, bundled
# user seed under data/).
COPY alembic.ini ./
COPY app ./app
COPY scripts ./scripts
COPY data ./data
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Create the data dir that Chroma writes into (mounted as a volume in compose).
RUN mkdir -p /data/vectorstore /data/uploads

EXPOSE 8000

# Healthcheck hits /healthz from the API itself.
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]