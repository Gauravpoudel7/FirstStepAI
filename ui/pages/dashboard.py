"""Dashboard page — Active Projects, Leave Balance, Upcoming Holidays, AI Usage."""
from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from auth.models import User
from services.document_service import recent_documents
from services.employee_service import get_employee_profile
from ui.components import render_metric_row


UPCOMING_HOLIDAYS = [
    ("New Year's Day", date(date.today().year + 1, 1, 1)),
    ("Umbrella Foundation Day", date(date.today().year, 12, 1)),
    ("Raccoon City Memorial", date(date.today().year, 9, 30)),
    ("Winter Solstice", date(date.today().year, 12, 21)),
]


def _next_holiday() -> tuple[str, int]:
    today = date.today()
    upcoming = sorted(
        [(name, d) for name, d in UPCOMING_HOLIDAYS if d >= today],
        key=lambda x: x[1],
    )
    if not upcoming:
        return ("—", 0)
    name, d = upcoming[0]
    return (name, (d - today).days)


def render_dashboard(user: User) -> None:
    profile = get_employee_profile(user)
    ai_msgs = sum(1 for m in st.session_state.get("messages", []) if m.get("role") == "ai")

    next_holiday, days_until = _next_holiday()
    docs = recent_documents(user)

    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
          <h1 style="margin: 0; font-size: 1.75rem; letter-spacing: -0.02em;">
            Welcome back, {profile.full_name.split()[0]} 👋
          </h1>
          <p style="color: var(--text-secondary); margin: 0.25rem 0 0 0;">
            {profile.designation} · {profile.department} · {profile.office_location}
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metric_row(
        [
            {
                "label": "Active Projects",
                "value": len(profile.projects) or 0,
                "icon": "📂",
                "delta": (profile.projects[0] if profile.projects else "No projects assigned"),
            },
            {
                "label": "Leave Balance",
                "value": f"{profile.leave_balance} days",
                "icon": "🌴",
                "delta": f"Hire date: {profile.hire_date or 'N/A'}",
            },
            {
                "label": "Next Holiday",
                "value": next_holiday,
                "icon": "🎉",
                "delta": (f"in {days_until} days" if days_until else ""),
            },
            {
                "label": "AI Usage",
                "value": f"{ai_msgs} messages",
                "icon": "✨",
                "delta": "this session",
            },
        ]
    )

    # Quick actions
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='margin: 0 0 0.75rem 0; font-size: 1.1rem;'>Quick Actions</h3>",
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    actions = [
        ("💬", "Start Chat", "Chat"),
        ("📚", "Browse Policies", "Knowledge Base"),
        ("👤", "My Profile", "My Profile"),
        ("🔍", "Ask AI", "Chat"),
    ]
    for col, (icon, label, page) in zip(cols, actions):
        with col:
            if st.button(f"{icon}  {label}", key=f"qa_{label}", use_container_width=True):
                from core.session import get_session
                get_session().set_page(page)
                st.rerun()

    # Recent documents
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='margin: 0 0 0.75rem 0; font-size: 1.1rem;'>Recent Documents</h3>",
        unsafe_allow_html=True,
    )
    if not docs:
        st.info("No documents available for your role yet.")
    else:
        for d in docs:
            st.markdown(
                f"""
                <div class="glass" style="padding: 0.85rem 1rem; margin-bottom: 0.6rem;">
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                      <div style="font-weight: 600; color: var(--text-primary);">{d['title']}</div>
                      <div style="color: var(--text-secondary); font-size: 0.85rem;">{d['summary']}</div>
                    </div>
                    <div style="display: flex; gap: 0.4rem;">
                      <span style="font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 999px;
                                   background: var(--accent-soft); color: var(--accent); font-weight: 600;">
                        {d['doc_type']}
                      </span>
                      <span style="font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 999px;
                                   background: var(--bg-tertiary); color: var(--text-secondary); font-weight: 600;">
                        {d['department']}
                      </span>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
