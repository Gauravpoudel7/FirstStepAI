"""Chat service — owns the LCEL chain, employee context, and role-aware retriever."""
from __future__ import annotations

from typing import Iterator, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from auth.models import User
from prompts.system import SYSTEM_PROMPT
from config.settings import get_settings


def _history_to_messages(history: list[dict]) -> list[BaseMessage]:
    out: list[BaseMessage] = []
    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            out.append(HumanMessage(content=content))
        elif role == "ai":
            out.append(AIMessage(content=content))
    return out


class ChatService:
    """Owns the LangChain chain. Per-session instance."""

    def __init__(
        self,
        llm,
        retriever,
        employee_profile,
        system_prompt: str | None = None,
        company_name: str | None = None,
    ):
        self.llm = llm
        self.retriever = retriever
        self.employee_profile = employee_profile
        self.system_prompt = system_prompt or SYSTEM_PROMPT
        self.company_name = company_name or get_settings().COMPANY_NAME
        self.chain = self._build_chain()

    def _build_chain(self):
        prompt = ChatPromptTemplate(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder("conversation_history"),
                ("human", "{user_input}"),
            ]
        )

        def _retrieve(_: dict) -> str:
            try:
                # The retrieval query is the latest user message.
                return "\n\n---\n\n".join(
                    d.page_content for d in self.retriever.invoke(self._last_user_input)
                )
            except Exception:
                return ""

        chain = (
            {
                "company_name": lambda _: self.company_name,
                "retrieved_policy_information": _retrieve,
                "employee_information": lambda _: self.employee_profile.to_readable_block(),
                "user_input": RunnablePassthrough(),
                "conversation_history": lambda x: _history_to_messages(self._history),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        return chain

    # ---------- streaming ----------

    _last_user_input: str = ""
    _history: list[dict] = []

    def stream(self, user_input: str, history: list[dict]) -> Iterator[str]:
        self._last_user_input = user_input
        self._history = history
        # The chain expects a string input that flows through `user_input`.
        return self.chain.stream(user_input)

    # ---------- user rebinding ----------

    def update_user(self, user: User, employee_profile) -> None:
        self.employee_profile = employee_profile
        if self.retriever is not None and hasattr(self.retriever, "update_user"):
            self.retriever.update_user(user)
