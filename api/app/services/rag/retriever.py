"""Role-aware retriever (ported verbatim from rag/retriever.py).

Wraps a Chroma vector store and injects `filter={"required_role": {"$in": …}}`
on every retrieve so out-of-scope documents never leak into the LLM context.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStoreRetriever
from pydantic import ConfigDict

from app.core.rbac import allowed_doc_roles
from app.models.user import User


class RoleAwareRetriever(BaseRetriever):
    """Wrap a base retriever and inject a Chroma `filter` for role metadata.

    Filter support is explicit and fail-closed: the only base retriever this
    codebase constructs is ``VectorStoreRetriever`` (via
    ``Chroma.as_retriever(search_kwargs={"k": ...})``). For that type the
    role filter is set on ``search_kwargs`` at retrieval time. Any other base
    retriever raises ``NotImplementedError`` from this wrapper — the previous
    implementation silently fell back to unfiltered retrieval on any
    signature mismatch, which is a security regression we will not paper
    over.
    """

    base_retriever: BaseRetriever
    user_role: str = "employee"
    k: int = 4
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @contextmanager
    def _with_filter(self, filt: dict) -> Iterator[None]:
        """Set ``search_kwargs['filter']`` on the base retriever, then restore."""
        base = self.base_retriever
        if not isinstance(base, VectorStoreRetriever):
            raise NotImplementedError(
                f"RoleAwareRetriever requires a VectorStoreRetriever base; "
                f"got {type(base).__name__}. Refusing to retrieve without "
                f"role filtering."
            )
        prev = base.search_kwargs
        base.search_kwargs = {**(prev or {}), "filter": filt}
        try:
            yield
        finally:
            base.search_kwargs = prev

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        allowed = allowed_doc_roles(self.user_role)
        filt = {"required_role": {"$in": allowed}}
        with self._with_filter(filt):
            return self.base_retriever.invoke(query)

    async def _aget_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        allowed = allowed_doc_roles(self.user_role)
        filt = {"required_role": {"$in": allowed}}
        with self._with_filter(filt):
            return await self.base_retriever.ainvoke(query)

    def update_user(self, user: User) -> None:
        self.user_role = str(user.role)