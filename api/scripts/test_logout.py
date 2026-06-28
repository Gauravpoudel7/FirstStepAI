"""End-to-end logout flow check — login, /me, logout, /me-again."""
import json
import urllib.request
import http.cookiejar


def main() -> None:
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 1) Login
    payload = json.dumps(
        {"email": "demo@umbrella.corp", "password": "demo123", "remember_me": False}
    ).encode()
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    resp = opener.open(req, timeout=5)
    body = json.loads(resp.read())
    print("login:", resp.status, body["user"]["email"])
    print("cookies after login:", [c.name for c in cj])

    # 2) Hit /me (should succeed)
    req = urllib.request.Request("http://localhost:8000/api/v1/auth/me")
    resp = opener.open(req, timeout=5)
    print("me:", resp.status, json.loads(resp.read())["email"])

    # 3) Logout (should succeed)
    req = urllib.request.Request(
        "http://localhost:8000/api/v1/auth/logout",
        data=b"",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = opener.open(req, timeout=5)
    print("logout:", resp.status, json.loads(resp.read()))
    print("cookies after logout:", [c.name for c in cj])

    # 4) Hit /me again (should be 401 — cookie cleared)
    try:
        req = urllib.request.Request("http://localhost:8000/api/v1/auth/me")
        resp = opener.open(req, timeout=5)
        print("me after logout:", resp.status, "BUG — should be 401")
    except urllib.error.HTTPError as e:
        print("me after logout:", e.code, "(expected 401)")


if __name__ == "__main__":
    main()
