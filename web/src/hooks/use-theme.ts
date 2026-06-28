import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth.store";

/** Apply the persisted theme on mount and on every theme change. */
export function useTheme() {
  const theme = useAuthStore((s) => s.theme);
  const setTheme = useAuthStore((s) => s.setTheme);
  const toggle = useAuthStore((s) => s.toggleTheme);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.setAttribute("data-theme", theme);
      if (theme === "dark") document.documentElement.classList.add("dark");
      else document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  return { theme, setTheme, toggle };
}

/** Returns true once the component has mounted (avoids SSR hydration flicker). */
export function useMounted() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted;
}