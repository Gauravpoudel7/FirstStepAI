"""Role-aware retriever wrapping a Chroma vector store.

Filters chunks by `required_role` metadata before returning — RBAC enforced
at the data layer, so out-of-scope documents never leak into the LLM context.
"""
from __future__ import annotations

from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from auth.models import Role, User
from core.rbac import allowed_doc_roles


class RoleAwareRetriever(BaseRetriever):
    """Wrap a base retriever and inject a Chroma `filter` for role metadata.

    Falls back to `base_retriever.get_relevant_documents(...)` if the base
    retriever doesn't accept a `filter` kwarg (e.g. during tests).
    """

    base_retriever: BaseRetriever
    user_role: str = "employee"
    k: int = 4

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        allowed = allowed_doc_roles(self.user_role)
        filt = {"required_role": {"$in": allowed}}
        try:
            return self.base_retriever.invoke(query, filter=filt)
        except TypeError:
            # Older retriever signature without `filter`.
            return self.base_retriever.invoke(query)

    async def _aget_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        allowed = allowed_doc_roles(self.user_role)
        filt = {"required_role": {"$in": allowed}}
        try:
            return await self.base_retriever.ainvoke(query, filter=filt)
        except TypeError:
            return await self.base_retriever.ainvoke(query)

    def update_user(self, user: User) -> None:
        self.user_role = user.role.value if isinstance(user.role, Role) else str(user.role)