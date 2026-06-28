"""Login page (full screen)."""
from __future__ import annotations

import streamlit as st

from ui.theme import inject_login_css
from auth.ui import render_compact_login_form, render_forgot_password_dialog


def render_login_page() -> None:
    """Render the login page. Caller must `st.stop()` if no user is set."""
    inject_login_css()
    st.markdown("<div style='height: 4vh;'></div>", unsafe_allow_html=True)
    render_compact_login_form()

    # Forgot-password modal trigger (rendered below the form).
    st.markdown(
        "<div style='text-align: center; margin-top: 0.5rem;'>",
        unsafe_allow_html=True,
    )
    if st.button("Forgot password?", key="open_forgot_pw"):
        render_forgot_password_dialog()
    st.markdown("</div>", unsafe_allow_html=True)
