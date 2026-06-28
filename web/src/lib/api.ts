import axios, { type AxiosError, type AxiosRequestConfig } from "axios";
import { useAuthStore } from "@/store/auth.store";

// Axios `baseURL` is the path prefix prepended to every request. Callers pass
// full paths like "/api/v1/dashboard/summary", so baseURL must be "/" (not the
// /api/v1 prefix), otherwise paths get doubled up.
const envBase = import.meta.env.VITE_API_BASE_URL;
const baseURL =
  envBase && envBase !== "/api/v1"
    ? envBase // full backend origin (e.g. https://api.example.com) → strip /api/v1 from callers' paths too
    : "/";

export const api = axios.create({
  baseURL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

// 401 → try refresh → retry once. If refresh fails, hard logout.
let isRefreshing = false;
let pendingQueue: Array<() => void> = [];

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;
    const isAuthRoute =
      typeof original?.url === "string" &&
      (original.url.includes("/auth/login") ||
        original.url.includes("/auth/refresh") ||
        original.url.includes("/auth/forgot-password") ||
        original.url.includes("/auth/reset-password") ||
        original.url.includes("/auth/demo-accounts"));

    if (status === 401 && !original._retry && !isAuthRoute) {
      if (isRefreshing) {
        await new Promise<void>((resolve) => pendingQueue.push(resolve));
      } else {
        isRefreshing = true;
        try {
          await axios.post(`${envBase ?? "/api/v1"}/auth/refresh`, null, { withCredentials: true });
          pendingQueue.forEach((cb) => cb());
          pendingQueue = [];
        } catch (refreshErr) {
          // Resolve every queued waiter BEFORE clearing the array. The previous
          // implementation dropped `pendingQueue = []` with the resolvers still
          // attached, which meant every queued request's promise was never
          // resolved or rejected — those callers hung forever and the page
          // state stayed "loading" until a hard reload. Resolving the
          // waiters here lets each request's own 401 bubble up (and the page
          // handles them through the auth store).
          const waiters = pendingQueue;
          pendingQueue = [];
          waiters.forEach((cb) => cb());
          // Hard logout. Clearing the persisted user is critical: zustand's
          // `persist` middleware rehydrates `user` from localStorage on the
          // next page load, so without this the LoginPage would see a stale
          // `user`, auto-navigate back to `/`, and re-trigger the 401 →
          // refresh → 401 loop. Calling `logout()` here drops both the
          // in-memory user and the localStorage entry, so /login renders
          // fresh and stays put.
          try {
            useAuthStore.getState().logout();
          } catch {
            // store not initialized (e.g. during SSR or tests) — fall through
          }
          window.location.href = "/login";
          return Promise.reject(refreshErr);
        } finally {
          isRefreshing = false;
        }
      }
      original._retry = true;
      return api.request(original);
    }
    return Promise.reject(error);
  },
);
