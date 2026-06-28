import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "dark" | "light";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  permissions: string[];
  must_reset_password: boolean;
  initials?: string;
  employee_profile?: Record<string, unknown> | null;
}

interface AuthState {
  user: User | null;
  theme: Theme;
  setUser: (user: User | null) => void;
  setTheme: (t: Theme) => void;
  toggleTheme: () => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      theme: "dark",
      setUser: (user) => set({ user }),
      setTheme: (theme) => {
        if (typeof document !== "undefined") {
          document.documentElement.setAttribute("data-theme", theme);
          if (theme === "dark") document.documentElement.classList.add("dark");
          else document.documentElement.classList.remove("dark");
        }
        set({ theme });
      },
      toggleTheme: () =>
        set((state) => {
          const next: Theme = state.theme === "dark" ? "light" : "dark";
          if (typeof document !== "undefined") {
            document.documentElement.setAttribute("data-theme", next);
            if (next === "dark") document.documentElement.classList.add("dark");
            else document.documentElement.classList.remove("dark");
          }
          return { theme: next };
        }),
      logout: () => {
        // Clear the persisted slice so a refresh on /login doesn't briefly
        // rehydrate a stale user from localStorage. `partialize` keeps
        // `theme`; the `user` field is what we want gone.
        set({ user: null });
        if (typeof window !== "undefined") {
          try {
            useAuthStore.persist.clearStorage();
          } catch {
            // localStorage may be unavailable in some test environments
          }
        }
      },
    }),
    {
      name: "firststepai-auth",
      partialize: (s) => ({ theme: s.theme, user: s.user }),
    },
  ),
);