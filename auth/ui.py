"""Auth UI helpers — login form, forgot-password modal.

The actual login *page chrome* (the glassmorphism card, demo accounts) lives
in `ui.pages.login` and `ui.components.render_login_card`. This module owns
the form widgets and the dialog, which are called from those.
"""
from __future__ import annotations

import streamlit as st

from auth.services import get_auth_service
from core.exceptions import (
    InvalidCredentialsError,
    TokenExpiredError,
    TokenInvalidError,
    UserNotFoundError,
)


def render_compact_login_form() -> bool:
    """Render the login form. Returns True if the user was just authenticated."""
    svc = get_auth_service()

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="you@umbrella.corp", key="login_email")
        password = st.text_input(
            "Password", type="password", placeholder="••••••••", key="login_password"
        )
        col_remember, col_forgot = st.columns([1, 1])
        with col_remember:
            remember = st.checkbox("Remember me", value=False, key="login_remember")
        with col_forgot:
            st.markdown(
                "<div style='text-align:right; padding-top: 0.4rem;'></div>",
                unsafe_allow_html=True,
            )
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        try:
            user = svc.login(email, password, remember=remember)
        except InvalidCredentialsError as exc:
            st.error(str(exc))
            return False
        from core.session import get_session
        get_session().login_user(user, remember=remember)
        st.success(f"Welcome back, {user.full_name}.")
        st.rerun()
    return False


def render_forgot_password_dialog() -> None:
    """Open the forgot-password flow inside a Streamlit modal."""
    svc = get_auth_service()

    @st.dialog("Reset your password", width="small")
    def _dialog():
        st.write(
            "Enter the email tied to your account. We'll generate a reset link. "
            "*(Demo: the link is shown below instead of being emailed.)*"
        )
        email = st.text_input("Email", key="reset_email")
        submitted = st.button("Send reset link", use_container_width=True)
        if submitted:
            try:
                token = svc.request_password_reset(email)
            except UserNotFoundError as exc:
                st.warning(str(exc))
                return
            st.session_state["_reset_token"] = token
            st.session_state["_reset_email"] = email
            st.success("Reset link generated.")
            st.rerun()

        if st.session_state.get("_reset_token"):
            token = st.session_state["_reset_token"]
            st.info("Paste this token into the field below to complete the reset.")
            st.code(token, language="text")
            new_pw = st.text_input("New password", type="password", key="new_pw_1")
            new_pw2 = st.text_input("Confirm new password", type="password", key="new_pw_2")
            if st.button("Set new password", use_container_width=True):
                if not new_pw or new_pw != new_pw2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        svc.confirm_password_reset(token, new_pw)
                    except (TokenExpiredError, TokenInvalidError, InvalidCredentialsError) as exc:
                        st.error(str(exc))
                    else:
                        st.success("Password updated. You can now sign in.")
                        st.session_state.pop("_reset_token", None)
                        st.session_state.pop("_reset_email", None)

    _dialog()