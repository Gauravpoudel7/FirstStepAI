import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Save, Languages, Sparkles, Bell } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useTheme } from "@/hooks/use-theme";
import type { SettingsOut } from "@/lib/types";
import type { Theme } from "@/store/auth.store";

const LANGS = [
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "ja", label: "日本語" },
];

export default function SettingsPage() {
  const { setTheme } = useTheme();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery<SettingsOut>({
    queryKey: ["settings"],
    queryFn: async () => (await api.get("/api/v1/settings")).data,
  });

  const [theme, setLocalTheme] = useState<Theme>("dark");
  const [language, setLanguage] = useState("en");
  const [telemetry, setTelemetry] = useState(false);
  const [notifEmail, setNotifEmail] = useState(true);
  const [notifPush, setNotifPush] = useState(false);

  useEffect(() => {
    if (data) {
      const t: Theme = data.theme === "light" ? "light" : "dark";
      setLocalTheme(t);
      setLanguage(data.language);
      setTelemetry(data.anonymized_telemetry);
      const prefs = (data.notification_prefs as Record<string, boolean>) || {};
      setNotifEmail(prefs.email !== false);
      setNotifPush(!!prefs.push);
    }
  }, [data]);

  const save = useMutation({
    mutationFn: async () =>
      (
        await api.patch("/api/v1/settings", {
          theme,
          language,
          anonymized_telemetry: telemetry,
          notification_prefs: { email: notifEmail, push: notifPush },
        })
      ).data as SettingsOut,
    onSuccess: (s) => {
      qc.setQueryData(["settings"], s);
      setTheme(s.theme === "light" ? "light" : "dark");
      toast.success("Settings saved");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Save failed"),
  });

  if (isLoading) {
    return <div className="text-sm text-muted-foreground">Loading settings…</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground">
          Theme, language, and notification preferences — persisted to your account.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" /> Appearance
            </CardTitle>
            <CardDescription>Choose your theme.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label>Theme</Label>
              <div className="flex gap-2">
                {(["dark", "light"] as const).map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setLocalTheme(t)}
                    className={`flex-1 rounded-lg border px-4 py-3 text-sm capitalize transition ${
                      theme === t
                        ? "border-brand bg-brand/10 text-foreground"
                        : "border-border bg-secondary/40 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-1">
              <Label htmlFor="lang" className="flex items-center gap-2">
                <Languages className="h-3.5 w-3.5" /> Language
              </Label>
              <select
                id="lang"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm"
              >
                {LANGS.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-4 w-4" /> Notifications & telemetry
            </CardTitle>
            <CardDescription>
              We never sell your data. Anonymized telemetry helps us improve.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2">
              <div>
                <div className="text-sm font-medium">Email notifications</div>
                <div className="text-xs text-muted-foreground">
                  Updates about your conversations.
                </div>
              </div>
              <input
                type="checkbox"
                checked={notifEmail}
                onChange={(e) => setNotifEmail(e.target.checked)}
                className="h-4 w-4 accent-brand"
              />
            </label>
            <label className="flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2">
              <div>
                <div className="text-sm font-medium">Push notifications</div>
                <div className="text-xs text-muted-foreground">
                  Real-time alerts in your browser.
                </div>
              </div>
              <input
                type="checkbox"
                checked={notifPush}
                onChange={(e) => setNotifPush(e.target.checked)}
                className="h-4 w-4 accent-brand"
              />
            </label>
            <label className="flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2">
              <div>
                <div className="text-sm font-medium">Anonymized telemetry</div>
                <div className="text-xs text-muted-foreground">
                  Share anonymous usage statistics.
                </div>
              </div>
              <input
                type="checkbox"
                checked={telemetry}
                onChange={(e) => setTelemetry(e.target.checked)}
                className="h-4 w-4 accent-brand"
              />
            </label>
          </CardContent>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button onClick={() => save.mutate()} disabled={save.isPending}>
          <Save className="mr-2 h-4 w-4" />
          {save.isPending ? "Saving…" : "Save changes"}
        </Button>
      </div>
    </motion.div>
  );
}