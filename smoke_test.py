"""Smoke test for the FirstStepAI Streamlit app.

Drives the running app at http://localhost:8765:
  1. Loads the login page.
  2. Submits demo@umbrella.corp / demo123.
  3. Verifies the dashboard renders with the seeded employee's name.

Saves screenshots to /tmp/screenshots/ and prints PASS/FAIL.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Force UTF-8 stdout for Windows console compatibility.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


SCREENSHOT_DIR = Path("/tmp/screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:8765/"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()

        # Collect console messages for debugging.
        page.on("console", lambda msg: print(f"  [console.{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: print(f"  [pageerror] {exc}"))

        print(f"[1] Navigating to {URL}")
        page.goto(URL, wait_until="domcontentloaded", timeout=30000)

        # Wait for the login form to render (Streamlit hydrates via WebSocket).
        try:
            page.wait_for_selector("input[type='password']", timeout=20000)
            print("[2] Login form rendered OK")
        except PWTimeout:
            page.screenshot(path=str(SCREENSHOT_DIR / "01_no_login_form.png"), full_page=True)
            print("[2] FAIL: login form did not render in 20s")
            return 1

        page.screenshot(path=str(SCREENSHOT_DIR / "01_login_page.png"), full_page=True)

        # Fill credentials.
        # Streamlit form inputs don't have stable labels/placeholders in some
        # versions — use the first text input + the password input.
        text_inputs = page.locator("input[type='text']")
        password_input = page.locator("input[type='password']")
        text_inputs.first.fill("demo@umbrella.corp")
        password_input.first.fill("demo123")
        print("[3] Filled credentials OK")
        page.screenshot(path=str(SCREENSHOT_DIR / "02_login_filled.png"), full_page=True)

        # Submit.
        page.get_by_role("button", name="Sign In").click()
        print("[4] Clicked Sign In")

        # Wait for the dashboard greeting ("Welcome back, ...") to appear.
        try:
            page.wait_for_selector("text=Welcome back", timeout=20000)
            print("[5] Dashboard rendered OK")
        except PWTimeout:
            page.screenshot(path=str(SCREENSHOT_DIR / "03_no_dashboard.png"), full_page=True)
            print("[5] FAIL: dashboard did not render")
            return 2

        # Verify the user's name shows.
        body_text = page.inner_text("body")
        if "Ada Wong" in body_text:
            print("[6] Logged-in user 'Ada Wong' visible OK")
        else:
            print("[6] FAIL: expected 'Ada Wong' in body text")
            print("--- body excerpt ---")
            print(body_text[:500])
            return 3

        page.screenshot(path=str(SCREENSHOT_DIR / "03_dashboard.png"), full_page=True)

        # Try navigating to Chat.
        page.get_by_text("Chat", exact=True).first.click()
        try:
            page.wait_for_selector("text=Ask anything", timeout=10000)
            print("[7] Chat page rendered OK")
        except PWTimeout:
            page.screenshot(path=str(SCREENSHOT_DIR / "04_no_chat.png"), full_page=True)
            print("[7] FAIL: chat page did not render")
            return 4
        page.screenshot(path=str(SCREENSHOT_DIR / "04_chat.png"), full_page=True)

        # Try the Knowledge Base.
        page.get_by_text("Knowledge Base", exact=True).first.click()
        try:
            page.wait_for_selector("text=available for your role", timeout=10000)
            print("[8] KB page rendered OK")
        except PWTimeout:
            page.screenshot(path=str(SCREENSHOT_DIR / "05_no_kb.png"), full_page=True)
            print("[8] FAIL: KB page did not render")
            return 5
        page.screenshot(path=str(SCREENSHOT_DIR / "05_kb.png"), full_page=True)

        # Profile.
        page.get_by_text("My Profile", exact=True).first.click()
        try:
            page.wait_for_selector("text=My Profile", timeout=10000)
            print("[9] Profile page rendered OK")
        except PWTimeout:
            print("[9] FAIL: profile page did not render")
            return 6
        page.screenshot(path=str(SCREENSHOT_DIR / "06_profile.png"), full_page=True)

        browser.close()
    print("=== PASS ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())