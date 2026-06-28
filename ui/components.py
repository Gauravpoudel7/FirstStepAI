"""Reusable UI components — top nav, sidebar, metric cards, chat bubbles."""
from __future__ import annotations

import streamlit as st

from auth.models import User
from config.settings import get_settings
from core.rbac import role_badge_color


# ---------- top nav ----------

def render_top_nav(user: User, page_name: str) -> None:
    """Sticky top bar with branding, theme toggle, user chip, logout."""
    settings = get_settings()
    role_color = role_badge_color(user.role)
    initials = user.initials()

    st.markdown(
        f"""
        <div class="top-nav">
          <div class="brand">
            <img src="{settings.COMPANY_LOGO_URL}" alt="logo"/>
            <span>{settings.COMPANY_NAME} · AI Assistant</span>
            <span style="color: var(--text-muted); font-weight: 400; font-size: 0.85rem; margin-left: 0.5rem;">
              · {page_name}
            </span>
          </div>
          <div class="right">
            <span class="role-badge" style="background: {role_color};">{user.role.value}</span>
            <span class="user-chip">
              <span class="avatar">{initials}</span>
              <span style="font-size: 0.85rem; font-weight: 500;">{user.full_name}</span>
            </span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 1, 6, 1, 1])
    with cols[0]:
        if st.button("🌓 Theme", key="nav_theme", use_container_width=True, help="Toggle dark/light"):
            from core.session import get_session
            get_session().toggle_theme()
            st.rerun()
    with cols[3]:
        if st.button("🔄 Reset", key="nav_reset", use_container_width=True, help="Reset conversation"):
            for k in ("messages",):
                st.session_state.pop(k, None)
            st.rerun()
    with cols[4]:
        if st.button("↩ Logout", key="nav_logout", type="secondary", use_container_width=True):
            from core.session import get_session
            get_session().logout_user()
            st.rerun()


# ---------- sidebar ----------

def render_sidebar_nav(user: User) -> str:
    """Render the sidebar nav. Returns the selected page name."""
    from core.session import get_session
    from auth.models import Role

    settings = get_settings()
    pages = ["Dashboard", "Chat", "Knowledge Base", "My Profile"]
    if user.role == Role.ADMIN:
        pages.append("Admin")

    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem 0;">
              <img src="{settings.COMPANY_LOGO_URL}" style="width: 64px; height: 64px; filter: drop-shadow(0 4px 12px rgba(124,58,237,0.4));"/>
              <div style="font-weight: 700; margin-top: 0.5rem; font-size: 1.05rem;">{settings.COMPANY_NAME}</div>
              <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.15rem;">AI Assistant · v1.0</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        role_color = role_badge_color(user.role)
        st.markdown(
            f"""
            <div class="user-chip" style="margin: 0.5rem 0 1rem 0; padding: 0.5rem 0.75rem 0.5rem 0.5rem;">
              <span class="avatar">{user.initials()}</span>
              <div style="display: flex; flex-direction: column;">
                <span style="font-size: 0.85rem; font-weight: 600;">{user.full_name}</span>
                <span class="role-badge" style="background: {role_color}; align-self: flex-start; margin-top: 0.2rem;">{user.role.value}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        current = get_session().get_page()
        try:
            idx = pages.index(current)
        except ValueError:
            idx = 0
        choice = st.radio("Navigate", pages, index=idx, key="page_radio", label_visibility="collapsed")
        if choice != current:
            get_session().set_page(choice)
            st.rerun()

        st.markdown("---")
        st.markdown(
            "<div style='color: var(--text-muted); font-size: 0.7rem; text-align: center;'>"
            "© 2026 Umbrella Corporation<br/>Internal use only"
            "</div>",
            unsafe_allow_html=True,
        )
    return get_session().get_page()


# ---------- metric card ----------

def render_metric_card(label: str, value, icon: str, delta: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="icon">{icon}</div>
          <div class="label">{label}</div>
          <div class="value">{value}</div>
          <div class="delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_row(cards: list[dict]) -> None:
    """Render a row of metric cards. `cards` is a list of dicts with
    {label, value, icon, delta}."""
    cols = st.columns(len(cards))
    for col, c in zip(cols, cards):
        with col:
            render_metric_card(c["label"], c["value"], c["icon"], c.get("delta", ""))


# ---------- chat bubble (with markdown + code blocks) ----------

def render_chat_bubble(role: str, content: str, msg_id: str | None = None,
                      show_feedback: bool = False) -> None:
    """Render a single chat bubble with custom HTML/CSS.

    `role` is 'user' or 'ai'. For 'ai' messages, pass `msg_id` and
    `show_feedback=True` to render thumbs up/down buttons.
    """
    from utils.markdown import highlight_code_blocks

    safe = highlight_code_blocks(content)
    cls = "user" if role == "user" else "ai"
    label = "You" if role == "user" else "AI"
    avatar_text = "🧑" if role == "user" else "⛛"
    avatar_bg = "var(--accent)" if role == "user" else "var(--bg-tertiary)"

    st.markdown(
        f"""
        <div class="chat-row {cls}">
          <div class="avatar" style="background: {avatar_bg}; flex-shrink: 0; align-self: flex-end;">
            {avatar_text}
          </div>
          <div class="chat-bubble">
            <div style="font-size: 0.7rem; font-weight: 600; opacity: 0.7; margin-bottom: 0.35rem;">{label}</div>
            {safe}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_feedback and msg_id:
        from services.feedback_service import record_feedback
        cols = st.columns([1, 1, 8])
        with cols[0]:
            if st.button("👍", key=f"fb_up_{msg_id}", help="Helpful response"):
                record_feedback(msg_id, "up")
                st.toast("Thanks for the feedback!", icon="👍")
        with cols[1]:
            if st.button("👎", key=f"fb_dn_{msg_id}", help="Not helpful"):
                record_feedback(msg_id, "down")
                st.toast("Feedback recorded.", icon="👎")


# ---------- suggested prompt chips ----------

def render_suggested_prompts(prompts: list[str], key_prefix: str) -> None:
    """Render clickable prompt suggestions. Stores the chosen prompt in
    `st.session_state[f"{key_prefix}_picked"]` for the chat page to pick up."""
    if not prompts:
        return
    st.markdown(
        "<div style='margin: 0.5rem 0; color: var(--text-muted); font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;'>Try asking</div>",
        unsafe_allow_html=True,
    )
    cols = st.columns(min(len(prompts), 3))
    for col, p in zip(cols, prompts[:3]):
        with col:
            if st.button(p, key=f"{key_prefix}_{hash(p)}", use_container_width=True):
                st.session_state["pending_prompt"] = p
                st.rerun()


# ---------- login page ----------

def render_login_styles() -> None:
    """No-op placeholder — kept for symmetry; styles live in base.css."""
    return None


def render_login_card(form_renderer, demo_accounts: list[dict], default_password: str) -> None:
    """Render the full-page login card. `form_renderer` is a callable that
    draws the actual `st.form`; we wrap it with the surrounding chrome."""
    settings = get_settings()
    st.markdown(
        f"""
        <div class="login-shell">
          <div class="login-card">
            <div class="brand-block">
              <img src="{settings.COMPANY_LOGO_URL}" alt="logo"/>
              <h1>{settings.COMPANY_NAME}</h1>
              <p>AI Assistant · Sign in to continue</p>
            </div>
        """,
        unsafe_allow_html=True,
    )

    form_renderer()

    demo_html = "".join(
        f'<div class="demo-row"><span><code>{acc["email"]}</code></span><span style="color: var(--text-muted);">{acc["role"]}</span></div>'
        for acc in demo_accounts
    )
    st.markdown(
        f"""
            <div class="demo-expander">
              <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.4rem;">
                🔐 Demo accounts
              </div>
              <div style="color: var(--text-muted); margin-bottom: 0.5rem;">
                Password for all: <code>{default_password}</code>
              </div>
              {demo_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
