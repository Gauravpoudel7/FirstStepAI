"""Document loaders (ported from rag/loader.py)."""
from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_core.documents import Document


def load_pdf(path: str | Path) -> List[Document]:
    from langchain_community.document_loaders import PyPDFLoader

    return PyPDFLoader(str(path)).load()


def load_text(path: str | Path) -> List[Document]:
    from langchain_community.document_loaders import TextLoader

    return TextLoader(str(path), encoding="utf-8").load()
