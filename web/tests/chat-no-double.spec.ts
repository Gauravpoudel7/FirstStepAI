/**
 * Regression test for "ChatAI gives two answers".
 *
 * Server-side is clean — one HTTP request returns one SSE stream with one
 * `done` event. The duplication was entirely client-side, from two bugs
 * that compounded in dev (StrictMode):
 *
 *   1. `ChatPage.submit` finalized the assistant bubble after `await send`
 *      resolved, using a render-time `messageId` capture that was `null`
 *      at that point — so `finalizeAssistant` failed to match and pushed
 *      a duplicate bubble.
 *   2. React 18 StrictMode double-invoked `submit`, opening two parallel
 *      SSE streams racing into the same store.
 *
 * Fix:
 *   - `useChatStream.send` is now single-flight (aborts the previous
 *     controller before opening a new POST) and surfaces the real
 *     `done`-frame ids through an `onDone` callback.
 *   - `ChatPage.submit` calls `onDone` to finalize the streaming bubble
 *     with the actual server ids, and uses a ref guard so the second
 *     StrictMode invocation no-ops before pushing a duplicate user bubble.
 *   - `chat.store.finalizeAssistant` is index-based: stamps the trailing
 *     assistant bubble in place, instead of pushing a duplicate on id miss.
 *
 * This test sends one message and asserts exactly one user bubble + one
 * assistant bubble appear, with no duplicates.
 */
import { test, expect } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL ?? "http://localhost:8080";
const EMAIL = process.env.E2E_EMAIL ?? "demo@umbrella.corp";
const PASSWORD = process.env.E2E_PASSWORD ?? "demo123";

test.describe.configure({ mode: "serial" });

test("chat: one user + one assistant per submit, no duplicates", async ({
  page,
}) => {
  page.on("pageerror", () => undefined);

  // Login
  await page.goto(`${BASE_URL}/login`);
  await page.locator('input[type="email"]').fill(EMAIL);
  await page.locator('input[type="password"]').fill(PASSWORD);
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(
    page.getByRole("heading", { name: /welcome back,/i })
  ).toBeVisible({ timeout: 15_000 });

  // Navigate to AI Chat
  await page.getByRole("link", { name: /ai chat/i }).click();
  await expect(page.getByText(/ask anything/i).first()).toBeVisible({
    timeout: 10_000,
  });

  // Send one message and wait for the assistant to finish.
  await page.locator('input[type="text"]').fill("hi");
  await page.getByRole("button", { name: /send/i }).click();

  // Wait for the streaming indicator to disappear (stream finished).
  // The placeholder text changes from "Streaming response…" to
  // "Ask the assistant anything…" once streaming is false.
  await expect(
    page.locator('input[placeholder*="Ask the assistant"]')
  ).toBeVisible({ timeout: 30_000 });

  // Count bubbles. Scope to the chat scroll container so we don't catch the
  // brand-gradient logo box in the sidebar or the user-avatar pill in the
  // TopBar (both reuse `bg-brand-gradient`). The chat list is the only
  // scrollable element with `overflow-y-auto` inside `<main>`.
  const chatList = page.locator('main .overflow-y-auto');
  const userBubbles = chatList.locator(".bg-brand-gradient.text-white");
  const assistantBubbles = chatList.locator(
    ".bg-card.text-card-foreground.border",
  );

  await expect(userBubbles).toHaveCount(1);
  await expect(assistantBubbles).toHaveCount(1);
});
