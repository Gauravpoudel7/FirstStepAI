"""Document service — list, fetch, upload, delete, reindex.

Role filter is enforced here on top of the role-aware retriever: even though
the retriever filters at retrieval time, the documents API must also hide
chunks that the user can't see.
"""
from __future__ import annotations

import hashlib
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.rbac import allowed_doc_roles
from app.models.document import Document
from app.models.user import User
from app.services.rag import add_document_text, ensure_indexed, reindex_pdf


def list_visible_documents(db: Session, user: User) -> list[Document]:
    """List documents the user is permitted to see."""
    allowed = allowed_doc_roles(user.role)
    stmt = (
        select(Document)
        .where(Document.required_role.in_(allowed))
        .order_by(Document.created_at.desc())
    )
    return list(db.execute(stmt).scalars())


def get_document_for_user(db: Session, user: User, doc_id: str) -> Document | None:
    doc = db.get(Document, doc_id)
    if not doc:
        return None
    if doc.required_role not in allowed_doc_roles(user.role):
        # Hide existence from unauthorized users.
        return None
    return doc


def upload_text_document(
    db: Session,
    *,
    user: User,
    title: str,
    text: str,
    doc_type: str = "policy",
    department: str = "HR",
    required_role: str = "all",
) -> Document:
    """Ingest a text document, persist a Document row, and return it."""
    chunks = add_document_text(
        text,
        meta={
            "doc_type": doc_type,
            "department": department,
            "required_role": required_role,
        },
        source_name=title,
    )
    checksum = hashlib.sha256(text.encode("utf-8")).hexdigest()
    doc = Document(
        id=str(uuid.uuid4()),
        title=title,
        doc_type=doc_type,
        department=department,
        required_role=required_role,
        source_path=f"upload://{title}",
        checksum=checksum,
        chunk_count=chunks,
        indexed_at=None,
        uploaded_by=user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, user: User, doc_id: str) -> bool:
    """Delete a Document row. Only ADMIN may delete (RBAC checked upstream)."""
    doc = db.get(Document, doc_id)
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True


def reindex_all(db: Session, user: User) -> int:
    """Rebuild the vector store from the bundled PDF."""
    settings = get_settings()
    pdf_path = settings.policies_pdf
    if not pdf_path.exists():
        return 0
    chunks = reindex_pdf(pdf_path)
    # Refresh indexed_at for the matching Document row, if any.
    for d in db.execute(select(Document)).scalars():
        d.indexed_at = None
    db.commit()
    return chunks


def bootstrap_vectorstore() -> bool:
    """Lifespan helper: ensure the bundle PDF is indexed on startup."""
    return ensure_indexed()