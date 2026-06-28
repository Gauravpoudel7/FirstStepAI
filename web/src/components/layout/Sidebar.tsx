import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  BookOpen,
  Briefcase,
  FileText,
  BarChart3,
  History,
  Settings as SettingsIcon,
  UserCircle,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/store/auth.store";
import { useMounted } from "@/hooks/use-theme";

interface NavItem {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
  roles?: string[]; // roles allowed; undefined = everyone
}

const ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/chat", label: "AI Chat", icon: MessageSquare },
  { to: "/knowledge", label: "Knowledge Base", icon: BookOpen },
  { to: "/projects", label: "Projects", icon: Briefcase },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/history", label: "Chat History", icon: History },
  { to: "/profile", label: "Profile", icon: UserCircle },
  { to: "/admin", label: "Admin", icon: ShieldCheck, roles: ["admin"] },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export function Sidebar() {
  const user = useAuthStore((s) => s.user);
  const mounted = useMounted();
  const role = user?.role ?? "";

  const visible = ITEMS.filter(
    (item) => !item.roles || item.roles.includes(role),
  );

  return (
    <aside className="hidden md:flex md:w-64 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-xl">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-border">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-brand-gradient text-white shadow-soft">
          <Sparkles className="h-4 w-4" />
        </div>
        <div className="leading-tight">
          <div className="font-semibold">FirstStepAI</div>
          <div className="text-xs text-muted-foreground">Enterprise Suite</div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-1">
        {visible.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all",
                isActive
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
              )
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <motion.span
                    layoutId="sidebar-active"
                    className="absolute inset-y-1 left-0 w-1 rounded-r-full bg-brand-gradient"
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                )}
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-border text-xs text-muted-foreground">
        <div>v0.1.0</div>
        {mounted && <div>© {new Date().getFullYear()} Umbrella Corp.</div>}
      </div>
    </aside>
  );
}