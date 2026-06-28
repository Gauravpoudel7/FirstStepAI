"""FastAPI application entrypoint.

Wires:
  - CORS (per CORS_ORIGINS env var)
  - v1 router aggregator (/api/v1)
  - Health probe (/healthz)
  - Exception handlers that translate domain exceptions to HTTP responses
  - Lifespan: future phases mount vectorstore warmup + LLM service here
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import (
    AuthError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UnauthorizedError,
    UserNotFoundError,
)
from app.db.session import ensure_sqlite_schema
from app.services.document_service import bootstrap_vectorstore
from app.utils.logging import setup_logging

settings = get_settings()
setup_logging(level=settings.LOG_LEVEL)
log = logging.getLogger("firststepai.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # SQLite fallback: if the DB file is missing/empty, create the ORM tables
    # so the very first login request doesn't hang on a "no such table" error.
    if ensure_sqlite_schema():
        log.info("Bootstrapped SQLite schema from ORM metadata.")
    # Phase 4: ensure the bundled policies PDF is indexed at startup.
    bootstrap_vectorstore()
    yield


app = FastAPI(
    title="FirstStep AI",
    description="Enterprise AI assistant — FastAPI backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- exception handlers ----

@app.exception_handler(InvalidCredentialsError)
async def _invalid_credentials(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(TokenExpiredError)
async def _token_expired(_: Request, exc: TokenExpiredError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(TokenInvalidError)
async def _token_invalid(_: Request, exc: TokenInvalidError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
async def _user_not_found(_: Request, exc: UserNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedError)
async def _unauthorized(_: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exc)})


@app.exception_handler(AuthError)
async def _auth_error(_: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(RuntimeError)
async def _runtime_error(_: Request, exc: RuntimeError) -> JSONResponse:
    """Surface RAG / embedding errors with a useful detail instead of a bare 500.

    The RAG ingest path raises ``RuntimeError`` when embeddings are unconfigured
    (e.g. ``HF_TOKEN`` missing) so the operator gets a clear, actionable
    message. Without this handler FastAPI returns a 500 with an empty body
    and the toast in the Admin Console just says "Upload failed" with no
    context for the user.
    """
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc) or "Service temporarily unavailable"},
    )


# ---- routes ----

app.include_router(api_router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Lightweight health probe — used by docker-compose and load balancers."""
    return {"status": "ok"}