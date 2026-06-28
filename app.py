"""FirstStepAI — Enterprise AI Assistant entrypoint.

Orchestrates the boot sequence:
  1. Load settings + setup logging.
  2. Seed the demo user database (first run only).
  3. Bootstrap session from any remember-me token in the URL.
  4. Inject CSS + render either login page or the authenticated app shell.
"""
from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import logging  # noqa: E402

import streamlit as st  # noqa: E402

from auth.models import Role  # noqa: E402
from config.settings import get_settings  # noqa: E402
from core.session import get_session  # noqa: E402
from data.employees import seed_user_database  # noqa: E402
from ui.components import render_sidebar_nav, render_top_nav  # noqa: E402
from ui.pages.admin import render_admin  # noqa: E402
from ui.pages.chat import render_chat  # noqa: E402
from ui.pages.dashboard import render_dashboard  # noqa: E402
from ui.pages.knowledge_base import render_knowledge_base  # noqa: E402
from ui.pages.login import render_login_page  # noqa: E402
from ui.pages.profile import render_profile  # noqa: E402
from ui.theme import inject_css  # noqa: E402
from utils.logging import setup_logging  # noqa: E402


setup_logging()
log = logging.getLogger("firststepai")

# First-run setup: seed demo users + ensure vector store is built.
try:
    seeded = seed_user_database()
    if seeded:
        log.info("Seeded %s demo user(s).", seeded)
except Exception as e:  # noqa: BLE001
    log.exception("Failed to seed users: %s", e)

try:
    from rag.ingest import ensure_indexed
    if ensure_indexed():
        log.info("Vector store ready.")
    else:
        log.warning("Vector store not built (no PDF found).")
except Exception as e:  # noqa: BLE001
    log.exception("Vector store init failed: %s", e)


settings = get_settings()
st.set_page_config(
    page_title=f"{settings.COMPANY_NAME} · AI Assistant",
    page_icon=settings.COMPANY_FAVICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- bootstrap session ----------

session = get_session()
session.bootstrap_from_query_params()


# ---------- render ----------

if not session.is_authenticated():
    render_login_page()
    st.stop()

user = session.current_user()
assert user is not None

inject_css()
page = render_sidebar_nav(user)
render_top_nav(user, page)


RENDERERS = {
    "Dashboard": render_dashboard,
    "Chat": render_chat,
    "Knowledge Base": render_knowledge_base,
    "My Profile": render_profile,
    "Admin": render_admin,
}

try:
    RENDERERS[page](user)
except KeyError:
    render_dashboard(user)