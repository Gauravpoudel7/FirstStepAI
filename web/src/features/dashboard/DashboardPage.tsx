import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import {
  CalendarDays,
  Megaphone,
  MessagesSquare,
  Sparkles,
} from "lucide-react";
import { useAuthStore } from "@/store/auth.store";
import { api } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { firstName } from "@/lib/utils";
import type { DashboardSummaryOut } from "@/lib/types";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const profile = (user?.employee_profile ?? {}) as Record<string, any>;

  const { data: summary } = useQuery<DashboardSummaryOut>({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => (await api.get("/api/v1/dashboard/summary")).data,
    staleTime: 60_000,
  });

  const stats = [
    {
      label: "Leave balance",
      value: `${summary?.leave_balance ?? profile.leave_balance ?? 0} days`,
      icon: CalendarDays,
    },
    {
      label: "Active projects",
      value: String(summary?.active_projects ?? 0),
      icon: Sparkles,
    },
    {
      label: "Department",
      value: summary?.department || profile.department || "—",
      icon: Megaphone,
    },
    {
      label: "Role",
      value: summary?.role || user?.role || "—",
      icon: MessagesSquare,
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-semibold">
          Welcome back, {firstName(summary?.full_name || user?.full_name)} 👋
        </h1>
        <p className="text-muted-foreground">
          {summary?.designation || profile.designation || user?.email} •{" "}
          {summary?.department || profile.department}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label} className="glass">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between text-muted-foreground">
                <CardDescription>{s.label}</CardDescription>
                <s.icon className="h-4 w-4 opacity-70" />
              </div>
              <CardTitle className="text-2xl">{s.value}</CardTitle>
            </CardHeader>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Your projects</CardTitle>
            <CardDescription>
              Active initiatives you are on.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {(profile.projects as string[] | undefined)?.length ? (
              <ul className="space-y-2">
                {(profile.projects as string[]).map((p) => (
                  <li
                    key={p}
                    className="rounded-lg border border-border bg-secondary/40 px-3 py-2"
                  >
                    {p}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No projects assigned.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4" /> Upcoming holidays
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summary?.upcoming_holidays?.length ? (
              <ul className="space-y-2 text-sm">
                {summary.upcoming_holidays.map((h) => (
                  <li
                    key={h.date}
                    className="flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2"
                  >
                    <span>{h.name}</span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(h.date).toLocaleDateString()}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No upcoming holidays listed.
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      {summary?.announcements?.length ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Megaphone className="h-4 w-4" /> Announcements
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2">
            {summary.announcements.map((a) => (
              <div
                key={a.title}
                className="rounded-xl border border-border bg-secondary/40 p-4"
              >
                <div className="text-sm font-semibold">{a.title}</div>
                <p className="mt-1 text-xs text-muted-foreground">{a.body}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      ) : null}

      <Card className="glass">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" /> AI usage
          </CardTitle>
          <CardDescription>Your activity this week.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">
              Messages today
            </div>
            <div className="mt-1 text-2xl font-semibold">
              {summary?.ai_usage?.messages_today ?? 0}
            </div>
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted-foreground">
              Tokens this week
            </div>
            <div className="mt-1 text-2xl font-semibold">
              {summary?.ai_usage?.tokens_this_week ?? 0}
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}