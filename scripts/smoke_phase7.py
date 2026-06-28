#!/usr/bin/env python3
"""Phase 7 smoke test — projects CRUD, settings, admin role/log.

Hits the live FastAPI stack through the Vite preview reverse proxy at
http://localhost:8080. Asserts:
  * projects: create / list / update / delete (manager + admin)
  * settings: get defaults → patch theme → re-fetch reflects change
  * branding: public, no auth
  * admin/users + admin/activity-log: ADMIN only
  * RBAC: employee cannot create projects (403)
"""
from __future__ import annotations
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://localhost:8080/api/v1"


def http(method: str, path: str, body=None, cookies: dict | None = None, expect=200):
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if cookies:
        headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in cookies.items())
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = resp.read().decode()
            set_cookies = {}
            for hdr, val in resp.getheaders():
                if hdr.lower() == "set-cookie":
                    for piece in val.split(","):
                        if "=" in piece:
                            k, v = piece.strip().split("=", 1)
                            v = v.split(";", 1)[0]
                            set_cookies[k] = v
            return resp.status, json.loads(payload) if payload else {}, set_cookies
    except urllib.error.HTTPError as e:
        try:
            payload = json.loads(e.read().decode())
        except Exception:
            payload = {}
        return e.code, payload, {}


def login(email: str, password: str) -> dict:
    status, body, cookies = http("POST", "/auth/login", {"email": email, "password": password})
    assert status == 200, f"login {email}: {status} {body}"
    assert "access_token" in cookies, f"no access_token cookie for {email}: {cookies}"
    return cookies


passed = failed = 0


def check(label: str, cond: bool, detail: str = ""):
    global passed, failed
    if cond:
        print(f"  PASS {label}")
        passed += 1
    else:
        print(f"  FAIL {label} -- {detail}")
        failed += 1


def main() -> int:
    print("--- login 5 demo users ---")
    admin = login("admin@umbrella.corp", "demo123")
    hr = login("hr@umbrella.corp", "demo123")
    manager = login("manager@umbrella.corp", "demo123")
    employee = login("employee@umbrella.corp", "demo123")
    demo = login("demo@umbrella.corp", "demo123")
    check("5 demo users login OK", all([admin, hr, manager, employee, demo]))

    print("--- branding (public) ---")
    s, body, _ = http("GET", "/settings/branding")
    check("GET /settings/branding 200", s == 200, f"status={s}")
    check("company_name=Umbrella Corporation", body.get("company_name") == "Umbrella Corporation", str(body))

    print("--- projects: list (manager) ---")
    s, before, _ = http("GET", "/projects", cookies=manager)
    check("manager GET /projects 200", s == 200, f"status={s}")
    check("manager projects is list", isinstance(before, list))
    initial_count = len(before)

    print("--- projects: employee cannot create (403) ---")
    s, body, _ = http("POST", "/projects", {"name": "forbidden"}, cookies=employee, expect=403)
    check("employee POST /projects forbidden", s == 403, f"status={s} body={body}")

    print("--- projects: manager creates ---")
    s, created, _ = http(
        "POST",
        "/projects",
        {
            "name": "Smoke Phoenix",
            "description": "Phase 7 e2e",
            "tags": ["smoke", "phase7"],
            "member_ids": [],
        },
        cookies=manager,
    )
    check("manager POST /projects 201/200", s in (200, 201), f"status={s} body={created}")
    pid = created.get("id")
    check("project has id", bool(pid))
    check("project is member of itself (owner)", pid and created.get("owner_id") in (created.get("member_ids") or []))

    print("--- projects: update ---")
    s, updated, _ = http("PATCH", f"/projects/{pid}", {"name": "Smoke Phoenix v2", "status": "paused"}, cookies=manager)
    check("PATCH /projects/{id} 200", s == 200, f"status={s} body={updated}")
    check("project name updated", updated.get("name") == "Smoke Phoenix v2")
    check("project status updated", updated.get("status") == "paused")

    print("--- projects: get single ---")
    s, single, _ = http("GET", f"/projects/{pid}", cookies=manager)
    check("GET /projects/{id} 200", s == 200, f"status={s}")
    check("get returns matching name", single.get("name") == "Smoke Phoenix v2")

    print("--- projects: employee visibility ---")
    # employee is NOT a member → should not see
    s, _, _ = http("GET", f"/projects/{pid}", cookies=employee)
    check("employee GET /projects/{id} 404", s == 404, f"status={s}")

    print("--- projects: roster (manager) ---")
    s, roster, _ = http("GET", "/projects/employees/options", cookies=manager)
    check("GET /projects/employees/options 200", s == 200, f"status={s}")
    check("roster has at least 4 employees", len(roster) >= 4, str(len(roster)))

    print("--- projects: delete ---")
    s, _, _ = http("DELETE", f"/projects/{pid}", cookies=manager)
    check("DELETE /projects/{id} 204/200", s in (200, 204), f"status={s}")
    s, after, _ = http("GET", "/projects", cookies=manager)
    check("list count back to baseline", len(after) == initial_count, f"before={initial_count} after={len(after)}")

    print("--- settings: defaults ---")
    s, settings, _ = http("GET", "/settings", cookies=demo)
    check("GET /settings 200", s == 200)
    check("default theme=dark", settings.get("theme") == "dark")
    check("default language=en", settings.get("language") == "en")

    print("--- settings: patch ---")
    s, patched, _ = http("PATCH", "/settings", {"theme": "light", "language": "fr"}, cookies=demo)
    check("PATCH /settings 200", s == 200, f"status={s} body={patched}")
    check("theme flipped to light", patched.get("theme") == "light")
    check("language flipped to fr", patched.get("language") == "fr")

    # restore
    http("PATCH", "/settings", {"theme": "dark", "language": "en"}, cookies=demo)

    print("--- admin: users list ---")
    s, users, _ = http("GET", "/admin/users", cookies=admin)
    check("admin GET /admin/users 200", s == 200, f"status={s}")
    check("5 users", len(users) == 5, str(len(users)))

    print("--- admin: non-admin blocked ---")
    s, _, _ = http("GET", "/admin/users", cookies=manager, expect=403)
    check("manager GET /admin/users 403", s == 403, f"status={s}")

    print("--- admin: activity-log ---")
    s, log, _ = http("GET", "/admin/activity-log", cookies=admin)
    check("admin GET /admin/activity-log 200", s == 200, f"status={s}")
    check("returns counts_by_action + recent", "counts_by_action" in log and "recent" in log)

    print("--- admin: role update ---")
    target = next(u for u in users if u["email"] == "employee@umbrella.corp")
    s, _, _ = http("PATCH", f"/admin/users/{target['id']}/role", {"role": "manager"}, cookies=admin)
    check("PATCH role 200", s == 200, f"status={s}")
    # restore
    http("PATCH", f"/admin/users/{target['id']}/role", {"role": "employee"}, cookies=admin)

    print()
    print(f"PASSED {passed} / FAILED {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())