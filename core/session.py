"""Session manager — wraps st.session_state + signed remember-me tokens.

Streamlit does not expose native server-side sessions or HttpOnly cookies.
We use:
  - `st.session_state` for the live (per-WebSocket) session.
  - `st.query_params["remember_token"]` as a poor-man's persistent token, signed
    with `itsdangerous`. On app boot, `bootstrap_from_query_params()` verifies
    the token and re-hydrates the user. Production deployments should put a
    reverse proxy in front of Streamlit that issues an HttpOnly cookie; that is
    out of scope here.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

from auth.models import User
from auth.security import sign_token, verify_token
from config.settings import get_settings


SESSION_KEY_USER = "authenticated_user"
SESSION_KEY_THEME = "theme"
SESSION_KEY_MESSAGES = "messages"
SESSION_KEY_CURRENT_PAGE = "current_page"
QUERY_PARAM_TOKEN = "remember_token"


class SessionManager:
    """Thin wrapper around `st.session_state` for auth state."""

    # ---------- current user ----------

    def current_user(self) -> Optional[User]:
        data = st.session_state.get(SESSION_KEY_USER)
        if not data:
            return None
        try:
            return User(**data)
        except Exception:
            st.session_state.pop(SESSION_KEY_USER, None)
            return None

    def is_authenticated(self) -> bool:
        return self.current_user() is not None

    def login_user(self, user: User, remember: bool = False) -> Optional[str]:
        st.session_state[SESSION_KEY_USER] = user.model_dump(mode="json")
        token: Optional[str] = None
        if remember:
            token = sign_token({"uid": user.id}, max_age=get_settings().REMEMBER_ME_MAX_AGE)
            st.session_state["_remember_token"] = token
            st.query_params[QUERY_PARAM_TOKEN] = token
        return token

    def logout_user(self) -> None:
        st.session_state.pop(SESSION_KEY_USER, None)
        st.session_state.pop(SESSION_KEY_MESSAGES, None)
        st.session_state.pop("_remember_token", None)
        if QUERY_PARAM_TOKEN in st.query_params:
            del st.query_params[QUERY_PARAM_TOKEN]

    # ---------- bootstrap from query params (remember-me) ----------

    def bootstrap_from_query_params(self) -> bool:
        """If a valid remember-me token is in the URL, re-hydrate the user.

        Returns True if a user was restored.
        """
        token = st.query_params.get(QUERY_PARAM_TOKEN)
        if not token:
            return False
        # Already authenticated? Nothing to do.
        if self.is_authenticated():
            return True
        payload = verify_token(token, max_age=get_settings().REMEMBER_ME_MAX_AGE)
        if not payload or "uid" not in payload:
            # Invalid or expired — clean up.
            if QUERY_PARAM_TOKEN in st.query_params:
                del st.query_params[QUERY_PARAM_TOKEN]
            return False
        # Resolve the user from the auth provider via the service layer.
        from auth.services import get_auth_service  # local import to avoid cycle

        user = get_auth_service().get_user_by_id(payload["uid"])
        if not user:
            if QUERY_PARAM_TOKEN in st.query_params:
                del st.query_params[QUERY_PARAM_TOKEN]
            return False
        st.session_state[SESSION_KEY_USER] = user.model_dump(mode="json")
        return True

    # ---------- theme ----------

    def get_theme(self) -> str:
        return st.session_state.get(SESSION_KEY_THEME, get_settings().THEME)

    def set_theme(self, theme: str) -> None:
        st.session_state[SESSION_KEY_THEME] = theme

    def toggle_theme(self) -> str:
        new = "light" if self.get_theme() == "dark" else "dark"
        self.set_theme(new)
        return new

    # ---------- current page ----------

    def get_page(self) -> str:
        return st.session_state.get(SESSION_KEY_CURRENT_PAGE, "Dashboard")

    def set_page(self, page: str) -> None:
        st.session_state[SESSION_KEY_CURRENT_PAGE] = page


# Module-level singleton for convenience.
_session: Optional[SessionManager] = None


def get_session() -> SessionManager:
    global _session
    if _session is None:
        _session = SessionManager()
    return _session
