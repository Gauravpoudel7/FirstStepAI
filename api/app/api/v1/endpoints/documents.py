"""Document endpoints — list, fetch, upload, delete, reindex."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.user import User
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentOut(BaseModel):
    id: str
    title: str
    doc_type: str
    department: str
    required_role: str
    source_path: str | None = None
    chunk_count: int = 0
    indexed_at: str | None = None
    created_at: str

    @classmethod
    def from_orm_doc(cls, doc) -> "DocumentOut":
        return cls(
            id=doc.id,
            title=doc.title,
            doc_type=doc.doc_type,
            department=doc.department,
            required_role=doc.required_role,
            source_path=getattr(doc, "source_path", None),
            chunk_count=doc.chunk_count,
            indexed_at=doc.indexed_at.isoformat() if doc.indexed_at else None,
            created_at=doc.created_at.isoformat(),
        )


@router.get("", response_model=list[DocumentOut])
def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[DocumentOut]:
    docs = document_service.list_visible_documents(db, current_user)
    return [DocumentOut.from_orm_doc(d) for d in docs]


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(
    doc_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentOut:
    doc = document_service.get_document_for_user(db, current_user, doc_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")
    return DocumentOut.from_orm_doc(doc)


class DocumentUpload(BaseModel):
    title: str
    text: str
    doc_type: str = "policy"
    department: str = "HR"
    required_role: str = "all"


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    body: DocumentUpload,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentOut:
    if not body.title.strip() or not body.text.strip():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "title and text are required"
        )
    doc = document_service.upload_text_document(
        db,
        user=current_user,
        title=body.title.strip(),
        text=body.text,
        doc_type=body.doc_type,
        department=body.department,
        required_role=body.required_role,
    )
    return DocumentOut.from_orm_doc(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: str,
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    ok = document_service.delete_document(db, current_user, doc_id)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found")


@router.post("/reindex")
def reindex(
    current_user: Annotated[User, Depends(require_role("admin"))],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int | str]:
    chunks = document_service.reindex_all(db, current_user)
    return {"status": "ok", "chunks": chunks}