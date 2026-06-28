"""Admin page — user management and document upload (gated to Role.ADMIN)."""
from __future__ import annotations

import streamlit as st

from auth.models import Role, User
from auth.services import get_auth_service
from core.exceptions import UnauthorizedError
from rag.ingest import add_document_text


def render_admin(current_user: User) -> None:
    if current_user.role != Role.ADMIN:
        raise UnauthorizedError("Admin page requires Role.ADMIN.")

    svc = get_auth_service()

    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
          <h1 style="margin: 0; font-size: 1.75rem; letter-spacing: -0.02em;">Admin Console</h1>
          <p style="color: var(--text-secondary); margin: 0.25rem 0 0 0;">
            Manage users and upload knowledge-base documents.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_users, tab_docs = st.tabs(["👥 Users", "📄 Documents"])

    # ---------- Users ----------
    with tab_users:
        users = svc.list_users()
        st.markdown(f"<div style='margin-bottom: 0.5rem; color: var(--text-secondary);'>{len(users)} accounts</div>", unsafe_allow_html=True)
        for u in users:
            with st.container():
                cols = st.columns([3, 3, 2, 2])
                with cols[0]:
                    st.markdown(
                        f"<div style='font-weight: 600;'>{u.full_name}</div>"
                        f"<div style='color: var(--text-muted); font-size: 0.8rem;'>{u.email}</div>",
                        unsafe_allow_html=True,
                    )
                with cols[1]:
                    st.markdown(
                        f"<div style='font-size: 0.85rem; color: var(--text-secondary);'>"
                        f"{u.employee_profile.designation}<br/>"
                        f"<span style='color: var(--text-muted);'>{u.employee_profile.department}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with cols[2]:
                    new_role = st.selectbox(
                        "Role",
                        options=[r.value for r in Role],
                        index=[r.value for r in Role].index(u.role.value),
                        key=f"role_{u.id}",
                        label_visibility="collapsed",
                    )
                    if new_role != u.role.value:
                        if st.button("Save", key=f"save_role_{u.id}"):
                            ok = svc.update_user_role(u.id, new_role)
                            if ok:
                                st.success(f"Role for {u.full_name} updated to {new_role}.")
                            else:
                                st.error("Failed to update role.")
                with cols[3]:
                    st.markdown(
                        f"<span style='font-size: 0.75rem; color: var(--text-muted);'>{u.id}</span>",
                        unsafe_allow_html=True,
                    )
            st.markdown("<hr style='border: none; border-top: 1px solid var(--border); margin: 0.5rem 0;'/>", unsafe_allow_html=True)

    # ---------- Documents ----------
    with tab_docs:
        st.markdown(
            "<div style='color: var(--text-secondary); margin-bottom: 0.5rem;'>Upload a text or markdown document to the knowledge base. Documents are tagged with a required role so they are only retrievable by authorized employees.</div>",
            unsafe_allow_html=True,
        )
        with st.form("upload_doc_form"):
            title = st.text_input("Document title", placeholder="e.g. Travel Policy 2026")
            uploaded = st.file_uploader("File", type=["txt", "md"])
            doc_type = st.selectbox(
                "Document type",
                options=["policy", "handbook", "sop", "tech_doc", "announcement", "faq"],
                key="upload_type",
            )
            department = st.selectbox(
                "Department",
                options=["HR", "Engineering", "Finance", "Security", "Operations", "All"],
                key="upload_dept",
            )
            required_role = st.selectbox(
                "Required role to view",
                options=["all", "employee", "manager", "hr", "admin"],
                key="upload_role",
            )
            submitted = st.form_submit_button("Upload & index", use_container_width=True)
            if submitted:
                if not uploaded or not title:
                    st.error("Provide a title and a file.")
                else:
                    text = uploaded.read().decode("utf-8", errors="ignore")
                    meta = {
                        "doc_type": doc_type,
                        "department": department,
                        "required_role": required_role,
                        "title": title,
                    }
                    n = add_document_text(text, meta, source_name=uploaded.name)
                    st.success(f"Indexed {n} chunk(s) for '{title}'.")