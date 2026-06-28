"""Document ingestion with role-based metadata tagging (ported from rag/ingest.py)."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Optional

from langchain_core.documents import Document

from app.config import get_settings
from app.services.rag.embeddings import build_embeddings, is_zero_embeddings
from app.services.rag.loader import load_pdf
from app.services.rag.splitter import chunk_documents
from app.services.rag.vectorstore import build_vectorstore, load_vectorstore

logger = logging.getLogger(__name__)


DEFAULT_POLICY_META = {
    "doc_type": "policy",
    "department": "HR",
    "required_role": "all",
}


def _tag_metadata(docs: Iterable[Document], meta: dict) -> list[Document]:
    out: list[Document] = []
    for d in docs:
        d.metadata = {**d.metadata, **meta}
        out.append(d)
    return out


def _guard_real_embeddings(embeddings) -> None:
    """Refuse to operate if embeddings is the zero-vector stub.

    Cosine similarity between zero vectors is undefined, so Chroma returns
    ARBITRARY docs in undefined order — every retrieval hallucinates
    plausible-but-ungrounded text. Operators must set HF_TOKEN or
    explicitly opt in with RAG_ALLOW_ZERO_EMBEDDINGS=true.
    """
    if is_zero_embeddings(embeddings):
        settings = get_settings()
        if not settings.RAG_ALLOW_ZERO_EMBEDDINGS:
            raise RuntimeError(
                "Refusing to ingest with _ZeroEmbeddings: cosine similarity "
                "is undefined for zero vectors and Chroma would return "
                "arbitrary docs. Set HF_TOKEN to use a real embedding model, "
                "or set RAG_ALLOW_ZERO_EMBEDDINGS=true to acknowledge the "
                "unsafe fallback."
            )
        logger.warning(
            "ingest running with RAG_ALLOW_ZERO_EMBEDDINGS=true. "
            "Retrieval will return arbitrary chunks."
        )


def reindex_pdf(pdf_path: str | Path, meta: Optional[dict] = None) -> int:
    """Load, split, tag, and add the PDF to the vector store. Returns chunk count."""
    meta = {**DEFAULT_POLICY_META, **(meta or {})}
    raw_docs = load_pdf(pdf_path)
    chunks = chunk_documents(raw_docs)
    # Use the file stem as the source name (e.g. ``umbrella_corp_policies``)
    # so the chat UI shows a readable citation instead of an absolute path.
    # ``PyPDFLoader`` leaves ``source`` as the full file path by default;
    # normalize it here so the chat source chip and the doc title match.
    source_name = Path(pdf_path).stem
    for c in chunks:
        c.metadata["source"] = source_name
    chunks = _tag_metadata(chunks, meta)
    embeddings = build_embeddings()
    _guard_real_embeddings(embeddings)
    build_vectorstore(chunks, embeddings, persist=True)
    return len(chunks)


def add_document_text(text: str, meta: dict, source_name: str = "uploaded") -> int:
    """Add a single text document to the existing vector store with metadata."""
    doc = Document(page_content=text, metadata={"source": source_name, **meta})
    chunks = chunk_documents([doc])
    chunks = _tag_metadata(chunks, meta)
    embeddings = build_embeddings()
    _guard_real_embeddings(embeddings)
    vs = load_vectorstore(embeddings)
    vs.add_documents(chunks)
    return len(chunks)


def ensure_indexed() -> bool:
    """Build the vector store from the bundled PDF if it doesn't already exist."""
    settings = get_settings()
    persist = settings.vectorstore_path / "chroma.sqlite3"
    if persist.exists():
        return True
    pdf = settings.policies_pdf
    if not pdf.exists():
        return False
    reindex_pdf(pdf)
    return True
