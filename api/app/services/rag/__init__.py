"""RAG utilities — embeddings, vector store, splitter, retriever, ingestion."""
from app.services.rag.embeddings import build_embeddings
from app.services.rag.ingest import add_document_text, ensure_indexed, reindex_pdf
from app.services.rag.loader import load_pdf, load_text
from app.services.rag.retriever import RoleAwareRetriever
from app.services.rag.splitter import chunk_documents
from app.services.rag.vectorstore import build_vectorstore, load_vectorstore

__all__ = [
    "RoleAwareRetriever",
    "add_document_text",
    "build_embeddings",
    "build_vectorstore",
    "chunk_documents",
    "ensure_indexed",
    "load_pdf",
    "load_text",
    "load_vectorstore",
    "reindex_pdf",
]
