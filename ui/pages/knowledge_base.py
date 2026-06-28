"""Knowledge Base page — browse role-filtered documents."""
from __future__ import annotations

import streamlit as st

from auth.models import User
from services.document_service import list_accessible_documents


_TYPE_COLORS = {
    "policy": "#7c3aed",
    "handbook": "#3b82f6",
    "sop": "#10b981",
    "tech_doc": "#f59e0b",
    "announcement": "#ef4444",
    "faq": "#6366f1",
}


def _badge(text: str, color: str) -> str:
    return (
        f'<span style="font-size: 0.7rem; padding: 0.2rem 0.55rem; border-radius: 999px; '
        f'background: {color}22; color: {color}; font-weight: 600; text-transform: uppercase; '
        f'letter-spacing: 0.04em;">{text}</span>'
    )


def render_knowledge_base(user: User) -> None:
    docs = list_accessible_documents(user)

    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
          <h1 style="margin: 0; font-size: 1.75rem; letter-spacing: -0.02em;">Knowledge Base</h1>
          <p style="color: var(--text-secondary); margin: 0.25rem 0 0 0;">
            {len(docs)} document{"s" if len(docs) != 1 else ""} available for your role
            (<span style="text-transform: uppercase; font-weight: 600; color: var(--accent);">{user.role.value}</span>)
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_input("Search documents", placeholder="Type to filter…", key="kb_search")
    filtered = [
        d for d in docs
        if not query or query.lower() in (d["title"] + d["summary"] + d["department"]).lower()
    ]

    if not filtered:
        st.info("No documents match your search or are accessible to your role.")
        return

    for d in filtered:
        type_color = _TYPE_COLORS.get(d["doc_type"], "#9ca3af")
        st.markdown(
            f"""
            <div class="glass" style="padding: 1rem 1.25rem; margin-bottom: 0.75rem;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem;">
                <div style="flex: 1;">
                  <div style="font-weight: 600; color: var(--text-primary); font-size: 1.05rem; margin-bottom: 0.25rem;">
                    {d['title']}
                  </div>
                  <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.4;">
                    {d['summary']}
                  </div>
                  <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.4rem;">
                    Source: {d['source']}
                  </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.4rem; align-items: flex-end;">
                  {_badge(d['doc_type'], type_color)}
                  {_badge(d['department'], '#3b82f6')}
                  {_badge(d['required_role'], '#9ca3af')}
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Ask-the-AI shortcut for this doc.
        if st.button(f"Ask AI about this", key=f"kb_ask_{d['id']}", use_container_width=False):
            st.session_state["pending_prompt"] = (
                f"Summarize the document '{d['title']}' and answer any policy questions about it."
            )
            from core.session import get_session
            get_session().set_page("Chat")
            st.rerun()