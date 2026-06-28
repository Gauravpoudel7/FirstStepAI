"""Embedding model factory (ported from rag/embeddings.py)."""
from __future__ import annotations

import logging

from app.config import get_settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 384


def build_embeddings():
    """Return the HF inference-API embeddings used for both ingest and query.

    Falls back to a local deterministic stub if no HF_TOKEN is set — keeps the
    app importable in offline tests. Use ``is_zero_embeddings(emb)`` to detect
    the stub; ``ingest.py`` and ``chat_service.py`` use that flag to refuse to
    index or serve RAG results when no real model is available.

    Note: the token is read from ``Settings``, not ``os.environ``. The previous
    ``os.environ.get("HF_TOKEN")`` lookup silently fell through to the zero
    stub because ``pydantic-settings`` loads `.env` into a Python attribute
    but does not export it to ``os.environ`` — so even though ``HF_TOKEN``
    was present in ``api/.env``, the embeddings factory never saw it and
    every upload got a 500 from the safety guard.
    """
    settings = get_settings()
    token = settings.HF_TOKEN or ""
    if token:
        from langchain_huggingface import HuggingFaceEndpointEmbeddings

        # Field is `huggingfacehub_api_token` in current `langchain_huggingface`
        # (older releases accepted `huggingface_api_token`; that name now
        # raises "Extra inputs are not permitted" at construction).
        return HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=token,
        )

    # Minimal stub: deterministic 384-dim zero vectors. Important caveat:
    # cosine similarity between zero vectors is undefined (NaN), so Chroma
    # returns ARBITRARY `k` docs in undefined order. The chat service then
    # streams those arbitrary chunks as if they were grounded answers — a
    # silent hallucination factory. Operators must either set HF_TOKEN or set
    # RAG_ALLOW_ZERO_EMBEDDINGS=true to opt into this unsafe fallback.
    logger.warning(
        "HF_TOKEN not set — using _ZeroEmbeddings stub. "
        "Retrieval will return arbitrary chunks. Set HF_TOKEN or "
        "RAG_ALLOW_ZERO_EMBEDDINGS=true to acknowledge this fallback."
    )

    class _ZeroEmbeddings:
        _is_zero = True  # marker for is_zero_embeddings()

        def embed_documents(self, texts):  # type: ignore[override]
            return [[0.0] * EMBEDDING_DIM for _ in texts]

        def embed_query(self, text):  # type: ignore[override]
            return [0.0] * EMBEDDING_DIM

    return _ZeroEmbeddings()  # type: ignore[return-value]


def is_zero_embeddings(emb) -> bool:
    """Return True when ``emb`` is the zero-vector stub returned above."""
    return getattr(emb, "_is_zero", False)