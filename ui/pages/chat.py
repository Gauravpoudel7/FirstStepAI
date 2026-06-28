"""Chat page — streaming chat with employee context and role-aware RAG."""
from __future__ import annotations

import streamlit as st

from auth.models import User
from prompts.suggested import SUGGESTED_PROMPTS
from prompts.welcome import WELCOME_MESSAGE
from services.chat_service import ChatService
from services.employee_service import get_employee_profile
from ui.components import (
    render_chat_bubble,
    render_suggested_prompts,
)


def _build_chat_service(user: User) -> ChatService:
    """Lazy-construct (or re-bind) the ChatService for the current user."""
    cache_key = "_chat_service"
    cached = st.session_state.get(cache_key)
    if cached is not None and getattr(cached, "_for_user", None) == user.id:
        # Refresh the profile in case it changed.
        cached.update_user(user, get_employee_profile(user))
        return cached

    from rag.embeddings import build_embeddings
    from rag.ingest import ensure_indexed
    from rag.vectorstore import load_vectorstore
    from rag.retriever import RoleAwareRetriever
    from services.llm import build_llm

    ensure_indexed()
    embeddings = build_embeddings()
    vs = load_vectorstore(embeddings)
    base_retriever = vs.as_retriever(search_kwargs={"k": 4})
    retriever = RoleAwareRetriever(
        base_retriever=base_retriever,
        user_role=user.role.value,
    )

    llm = build_llm()
    profile = get_employee_profile(user)
    svc = ChatService(
        llm=llm,
        retriever=retriever,
        employee_profile=profile,
    )
    svc._for_user = user.id  # type: ignore[attr-defined]
    st.session_state[cache_key] = svc
    return svc


def render_chat(user: User) -> None:
    profile = get_employee_profile(user)

    # Init message history.
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "ai", "content": WELCOME_MESSAGE}]

    # ---------- header ----------
    st.markdown(
        f"""
        <div style="margin-bottom: 1rem;">
          <h1 style="margin: 0; font-size: 1.75rem; letter-spacing: -0.02em;">💬 Chat</h1>
          <p style="color: var(--text-secondary); margin: 0.25rem 0 0 0;">
            Ask anything about your work, projects, policies, or onboarding.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- chat history ----------
    msgs = st.session_state["messages"]
    for i, m in enumerate(msgs):
        msg_id = f"{m.get('role','x')}_{i}_{hash(m.get('content',''))}"
        if m["role"] == "user":
            render_chat_bubble("user", m["content"], msg_id=None, show_feedback=False)
        else:
            render_chat_bubble("ai", m["content"], msg_id=msg_id, show_feedback=True)

    # ---------- suggested prompts (only if no user msg yet) ----------
    user_has_chatted = any(m["role"] == "user" for m in msgs)
    if not user_has_chatted:
        role_suggestions = SUGGESTED_PROMPTS.get(user.role, SUGGESTED_PROMPTS.get(user.role.__class__("employee"), []))
        # role is a str enum; the dict uses Role enum — coerce if needed.
        from auth.models import Role
        role_enum = Role(user.role.value) if not isinstance(user.role, Role) else user.role
        suggestions = SUGGESTED_PROMPTS.get(role_enum, [])
        if suggestions:
            render_suggested_prompts(suggestions, key_prefix="chat_suggest")

    # ---------- input ----------
    pending = st.session_state.pop("pending_prompt", None)
    user_input = st.chat_input("Ask anything…", key="chat_input")
    if pending:
        user_input = pending

    if user_input:
        # Append user bubble optimistically.
        render_chat_bubble("user", user_input, msg_id=None, show_feedback=False)
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # Build / get service.
        chat = _build_chat_service(user)

        # Stream the response.
        try:
            with st.chat_message("ai"):
                placeholder = st.empty()
                buf = []
                for token in chat.stream(user_input, st.session_state["messages"]):
                    buf.append(token)
                    placeholder.markdown("".join(buf))
                response_text = "".join(buf)
        except Exception as e:  # noqa: BLE001
            from utils.logging import setup_logging
            import logging
            setup_logging()
            logging.exception("Chat error")
            response_text = f"⚠️ Sorry, something went wrong: {e}"

        msg_id = f"ai_{len(st.session_state['messages'])}_{hash(response_text)}"
        render_chat_bubble("ai", response_text, msg_id=msg_id, show_feedback=True)
        st.session_state["messages"].append({"role": "ai", "content": response_text})