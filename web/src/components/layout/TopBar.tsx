import { Moon, Sun, LogOut, RotateCcw } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { RoleBadge } from "@/components/layout/RoleBadge";
import { useAuthStore } from "@/store/auth.store";
import { useChatStore } from "@/store/chat.store";
import { useTheme } from "@/hooks/use-theme";
import { api } from "@/lib/api";

const TITLES: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "AI Chat",
  "/knowledge": "Knowledge Base",
  "/projects": "Projects",
  "/documents": "Documents",
  "/analytics": "Analytics",
  "/history": "Chat History",
  "/profile": "Profile",
  "/admin": "Admin",
  "/settings": "Settings",
};

export function TopBar() {
  const user = useAuthStore((s) => s.user);
  const theme = useAuthStore((s) => s.theme);
  const toggleTheme = useAuthStore((s) => s.toggleTheme);
  const logout = useAuthStore((s) => s.logout);
  const _mounted = useTheme();
  void _mounted;
  const location = useLocation();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const title = TITLES[location.pathname] ?? "FirstStep AI";

  const handleReset = async () => {
    // The active chat state lives in `useChatStore` (ChatPage consumes it via
    // 2.6), so invalidating only the conversations query does nothing visible
    // on `/chat`. Reset the chat store AND the server-side history in one shot.
    useChatStore.getState().reset();
    qc.invalidateQueries({ queryKey: ["conversations"] });
    qc.invalidateQueries({ queryKey: ["dashboard"] });
    toast("Conversation reset", { description: "Cleared the active chat." });
  };

  const handleLogout = async () => {
    try {
      // The backend returns cookie-clearing Set-Cookie headers regardless of
      // auth state, so a failed call here still leaves us logged out locally.
      await api.post("/api/v1/auth/logout");
    } catch {
      // best-effort — proceed with local cleanup even if the server is down
    }
    logout(); // clears user + persists (see auth.store.ts)
    qc.clear();
    useChatStore.getState().reset();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-border bg-background/70 px-4 md:px-6 py-3 backdrop-blur-xl">
      <div className="flex items-center gap-3 min-w-0">
        <h1 className="text-lg font-semibold truncate">{title}</h1>
        {user?.role && <RoleBadge role={user.role} />}
      </div>
      <div className="flex items-center gap-2">
        <Button
          size="icon"
          variant="ghost"
          aria-label="Toggle theme"
          onClick={() => toggleTheme()}
        >
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
        {location.pathname === "/chat" && (
          <Button size="icon" variant="ghost" aria-label="Reset conversation" onClick={handleReset}>
            <RotateCcw className="h-4 w-4" />
          </Button>
        )}
        {user && (
          <div className="flex items-center gap-2 pl-2 pr-1 py-1 rounded-full border border-border bg-card/60">
            <div className="grid h-7 w-7 place-items-center rounded-full bg-brand-gradient text-white text-xs font-semibold">
              {user.initials ?? "?"}
            </div>
            <span className="hidden sm:inline text-sm">{user.full_name}</span>
          </div>
        )}
        <Button size="icon" variant="ghost" aria-label="Logout" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}