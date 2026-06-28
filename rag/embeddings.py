"""Embedding model factory."""
from __future__ import annotations

import os

from langchain_huggingface import HuggingFaceEndpointEmbeddings


def build_embeddings() -> HuggingFaceEndpointEmbeddings:
    """Return the HF inference-API embeddings used for both ingest and query.

    Falls back to a local deterministic stub if no HF_TOKEN is set — keeps the
    app importable in offline tests.
    """
    token = os.environ.get("HF_TOKEN") or ""
    if token:
        return HuggingFaceEndpointEmbeddings(
            model="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=token,
        )
    # Minimal stub: deterministic 384-dim zero vectors — good enough to import
    # without raising, retriever just won't return useful results.
    class _ZeroEmbeddings:
        def embed_documents(self, texts):  # type: ignore[override]
            return [[0.0] * 384 for _ in texts]

        def embed_query(self, text):  # type: ignore[override]
            return [0.0] * 384

    return _ZeroEmbeddings()  # type: ignore[return-value]