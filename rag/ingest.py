"""Document ingestion with role-based metadata tagging."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from langchain_core.documents import Document

from rag.loader import load_pdf
from rag.splitter import chunk_documents
from rag.vectorstore import build_vectorstore, load_vectorstore
from rag.embeddings import build_embeddings


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


def reindex_pdf(pdf_path: str | Path, meta: Optional[dict] = None) -> int:
    """Load, split, tag, and add the PDF to the vector store. Returns chunk count."""
    meta = {**DEFAULT_POLICY_META, **(meta or {})}
    raw_docs = load_pdf(pdf_path)
    chunks = chunk_documents(raw_docs)
    chunks = _tag_metadata(chunks, meta)
    embeddings = build_embeddings()
    vs = build_vectorstore(chunks, embeddings, persist=True)
    return len(chunks)


def add_document_text(text: str, meta: dict, source_name: str = "uploaded") -> int:
    """Add a single text document to the existing vector store with metadata."""
    doc = Document(page_content=text, metadata={"source": source_name, **meta})
    chunks = chunk_documents([doc])
    chunks = _tag_metadata(chunks, meta)
    embeddings = build_embeddings()
    vs = load_vectorstore(embeddings)
    vs.add_documents(chunks)
    return len(chunks)


def ensure_indexed() -> bool:
    """Build the vector store from the bundled PDF if it doesn't already exist.

    Returns True if the store exists (either pre-existing or freshly built).
    """
    from config.settings import get_settings

    persist = Path(get_settings().VECTORSTORE_PATH) / "chroma.sqlite3"
    if persist.exists():
        return True
    pdf = Path(get_settings().POLICIES_PDF)
    if not pdf.exists():
        return False
    reindex_pdf(pdf)
    return True