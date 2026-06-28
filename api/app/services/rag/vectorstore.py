"""Chroma vector store factory (ported from rag/vectorstore.py)."""
from __future__ import annotations

import os
from pathlib import Path

from app.config import get_settings


def ensure_store_dir() -> Path:
    p = get_settings().vectorstore_path
    p.mkdir(parents=True, exist_ok=True)
    return p


def build_vectorstore(documents, embeddings, persist: bool = True):
    from langchain_chroma import Chroma

    persist_dir = str(ensure_store_dir()) if persist else None
    if (
        persist_dir
        and os.path.isdir(persist_dir)
        and os.path.isfile(os.path.join(persist_dir, "chroma.sqlite3"))
    ):
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
        )
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_dir,
    )


def load_vectorstore(embeddings):
    from langchain_chroma import Chroma

    persist_dir = str(ensure_store_dir())
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
