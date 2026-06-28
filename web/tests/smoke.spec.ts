import { test, expect } from "@playwright/test";

/**
 * Parity smoke test — reproduces the contract strings from the original
 * `smoke_test.py` against the new React + FastAPI stack:
 *
 *   1. login → "Welcome back, …"
 *   2. AI Chat page → "Ask anything"
 *   3. RAG greeting → "available for your role"
 *   4. Profile sidebar → "My Profile"
 */

test.describe.configure({ mode: "serial" });

const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:8080";
const EMAIL = process.env.E2E_EMAIL ?? "demo@umbrella.corp";
const PASSWORD = process.env.E2E_PASSWORD ?? "demo123";

test("login → dashboard greeting → chat → profile", async ({ page }) => {
  // Suppress uncaught console errors that come from dev-only warnings.
  page.on("pageerror", () => undefined);

  // 1) Login
  await page.goto(`${BASE_URL}/login`);
  await page.locator('input[type="email"]').fill(EMAIL);
  await page.locator('input[type="password"]').fill(PASSWORD);
  await page.getByRole("button", { name: /sign in/i }).click();

  // 2) Dashboard greeting — "Welcome back, …"
  await expect(
    page.getByRole("heading", { name: /welcome back,/i })
  ).toBeVisible({
    timeout: 15_000,
  });

  // 3) AI Chat page — "Ask anything"
  await page.getByRole("link", { name: /ai chat/i }).click();
  await expect(
    page.getByText(/ask anything/i).first()
  ).toBeVisible({ timeout: 10_000 });

  // Send a question and verify RAG greeting ("available for your role")
  // appears in the suggested-prompt copy on the empty state.
  await expect(
    page.getByText(/available for your role/i)
  ).toBeVisible({ timeout: 10_000 });

  // 4) Profile sidebar — "My Profile"
  await page.getByRole("link", { name: /^profile$/i }).first().click();
  await expect(
    page.getByRole("heading", { name: /my profile/i })
  ).toBeVisible({ timeout: 10_000 });
});