import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Loader2,
  Users,
  Clock,
} from "lucide-react";
import { api } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { ActivityLogSummary } from "@/lib/types";

const ACTION_COLORS: Record<string, string> = {
  login: "bg-emerald-500/20",
  logout: "bg-amber-500/20",
  role_update: "bg-rose-500/20",
  chat_message: "bg-blue-500/20",
  document_upload: "bg-violet-500/20",
  document_delete: "bg-zinc-500/20",
  reindex: "bg-cyan-500/20",
};

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery<ActivityLogSummary>({
    queryKey: ["admin", "activity-log"],
    queryFn: async () =>
      (await api.get("/api/v1/admin/activity-log")).data,
  });

  const { data: users } = useQuery({
    queryKey: ["admin", "users"],
    queryFn: async () => (await api.get("/api/v1/admin/users")).data,
  });

  const barChart = useMemo(() => {
    if (!data?.counts_by_action) return [];
    const max = Math.max(1, ...Object.values(data.counts_by_action));
    return Object.entries(data.counts_by_action)
      .sort((a, b) => b[1] - a[1])
      .map(([action, count]) => ({
        action,
        count,
        pct: Math.round((count / max) * 100),
      }));
  }, [data]);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" /> Loading analytics…
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-semibold">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          Activity counts and recent actions across the workspace.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="glass">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Activity className="h-3 w-3" /> Total events
            </CardDescription>
            <CardTitle className="text-3xl">{data?.total ?? 0}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="glass">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <Users className="h-3 w-3" /> Active users
            </CardDescription>
            <CardTitle className="text-3xl">{users?.length ?? 0}</CardTitle>
          </CardHeader>
        </Card>
        <Card className="glass">
          <CardHeader className="pb-2">
            <CardDescription className="flex items-center gap-1">
              <BarChart3 className="h-3 w-3" /> Distinct actions
            </CardDescription>
            <CardTitle className="text-3xl">
              {Object.keys(data?.counts_by_action ?? {}).length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Events by action</CardTitle>
          <CardDescription>
            Visualized as horizontal bars — top is the most frequent action.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {barChart.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No activity recorded yet. Events appear here as users work.
            </p>
          ) : (
            barChart.map((row) => (
              <div key={row.action} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-mono">{row.action}</span>
                  <span className="text-muted-foreground">{row.count}</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                  <div
                    className={`h-full ${ACTION_COLORS[row.action] ?? "bg-brand/60"}`}
                    style={{ width: `${row.pct}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-4 w-4" /> Recent activity
          </CardTitle>
          <CardDescription>
            Last 10 actions, newest first.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {data?.recent?.length ? (
            <ul className="divide-y divide-border">
              {data.recent.map((r) => (
                <li
                  key={r.id}
                  className="flex items-center justify-between py-2 text-sm"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-md px-2 py-0.5 text-xs font-mono ${
                        ACTION_COLORS[r.action] ?? "bg-secondary"
                      }`}
                    >
                      {r.action}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {r.resource_type ? `${r.resource_type} ${r.resource_id ?? ""}` : ""}
                    </span>
                  </div>
                  <time className="text-xs text-muted-foreground">
                    {new Date(r.created_at).toLocaleString()}
                  </time>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted-foreground">No recent events.</p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}