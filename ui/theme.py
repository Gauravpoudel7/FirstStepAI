"""Theme + CSS injection for the entire app."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from core.session import get_session

_STYLES_DIR = Path(__file__).parent / "styles"
_BASE_CSS = _STYLES_DIR / "base.css"


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def get_active_theme() -> str:
    return get_session().get_theme()


def inject_css() -> None:
    """Inject the base stylesheet + activate the current theme.

    Should be called once on every page render where the chrome is visible.
    The login page calls `inject_login_css` instead because it does not need
    the sidebar / top-nav styles.
    """
    theme = get_active_theme()
    css = _read(_BASE_CSS)
    # Active theme flag — base.css already keys everything on
    # `:root[data-theme="..."]`, so we just need to set the attribute.
    st.markdown(
        f"""
        <style>
        {css}
        </style>
        <script>
          (function() {{
            try {{
              document.documentElement.setAttribute('data-theme', '{theme}');
            }} catch (e) {{}}
          }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


def inject_login_css() -> None:
    """Inject the same stylesheet for the login page (without the app chrome)."""
    theme = get_active_theme()
    css = _read(_BASE_CSS)
    st.markdown(
        f"""
        <style>
        {css}
        /* hide sidebar + top padding on the login page */
        [data-testid="stSidebar"] {{ display: none; }}
        .main .block-container {{ padding-top: 0; max-width: 100%; }}
        </style>
        <script>
          (function() {{
            try {{ document.documentElement.setAttribute('data-theme', '{theme}'); }} catch (e) {{}}
          }})();
        </script>
        """,
        unsafe_allow_html=True,
    )