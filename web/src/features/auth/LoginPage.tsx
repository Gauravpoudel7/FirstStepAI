import { useEffect, useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { Sparkles, LogIn, KeyRound, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth.store";
import { useTheme } from "@/hooks/use-theme";
import type { DemoAccountRow } from "@/lib/types";
import { cn } from "@/lib/utils";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  useTheme();

  const { data: demoAccounts = [] } = useQuery<DemoAccountRow[]>({
    queryKey: ["auth", "demo-accounts"],
    queryFn: async () => (await api.get("/api/v1/auth/demo-accounts")).data,
    staleTime: 5 * 60_000,
  });

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("demo123");
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-navigate to the original destination when a user is present in the
  // store. The axios interceptor (see `web/src/lib/api.ts`) clears the
  // persisted user whenever /auth/refresh fails, so a stale localStorage
  // entry can't keep re-triggering this redirect after the cookies are gone.
  useEffect(() => {
    if (user) {
      const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname || "/";
      navigate(from, { replace: true });
    }
  }, [user, location.state, navigate]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post("/api/v1/auth/login", {
        email,
        password,
        remember_me: remember,
      });
      setUser(data.user);
      toast.success(`Welcome back, ${data.user.full_name.split(" ")[0]}!`);
      const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname || "/";
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const useDemo = (em: string) => {
    setEmail(em);
    setPassword("demo123");
  };

  return (
    <div className="min-h-screen w-full grid lg:grid-cols-2 bg-background">
      {/* Left: brand pane */}
      <motion.div
        initial={{ opacity: 0, x: -24 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
        className="relative hidden lg:flex flex-col justify-between p-12 overflow-hidden"
        style={{
          backgroundImage:
            "radial-gradient(60% 50% at 20% 20%, rgba(59,130,246,0.25) 0%, transparent 60%), radial-gradient(50% 60% at 80% 80%, rgba(139,92,246,0.25) 0%, transparent 60%)",
        }}
      >
        <div className="flex items-center gap-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-brand-gradient text-white shadow-soft">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <div className="font-semibold">FirstStepAI</div>
            <div className="text-xs text-muted-foreground">Enterprise Suite</div>
          </div>
        </div>
        <div className="space-y-4">
          <h1 className="text-4xl font-semibold leading-tight tracking-tight">
            Your enterprise <br />
            <span className="bg-brand-gradient bg-clip-text text-transparent">
              AI assistant
            </span>
            , secured for your team.
          </h1>
          <p className="text-muted-foreground max-w-md">
            Onboarding, HR policies, security, projects, and personalized answers —
            all gated by your role and permissions.
          </p>
        </div>
        <div className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} Umbrella Corporation
        </div>
      </motion.div>

      {/* Right: login form */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-center justify-center p-6 md:p-12"
      >
        <Card className="w-full max-w-md glass-strong">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <LogIn className="h-5 w-5" />
              Sign in
            </CardTitle>
            <CardDescription>Use one of the demo accounts below.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={submit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="username"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@umbrella.corp"
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-muted-foreground">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="rounded border-border bg-transparent"
                />
                Remember me
              </label>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm"
                >
                  <AlertCircle className="h-4 w-4 mt-0.5 shrink-0 text-destructive" />
                  <span>{error}</span>
                </motion.div>
              )}
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Signing in…" : "Sign in"}
              </Button>
              <div className="text-center text-xs">
                <Link
                  to="/forgot-password"
                  className="text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
            </form>

            <div className="mt-6">
              <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground mb-2">
                <KeyRound className="h-3.5 w-3.5" /> Demo accounts
              </div>
              <div className="grid gap-2">
                {demoAccounts.map((acc) => (
                  <button
                    key={acc.email}
                    type="button"
                    onClick={() => useDemo(acc.email)}
                    className={cn(
                      "flex items-center justify-between gap-3 rounded-lg border border-border bg-card/40 px-3 py-2 text-sm hover:border-primary/40 hover:bg-card/80 transition",
                    )}
                  >
                    <div className="flex flex-col text-left">
                      <span className="font-medium">{acc.full_name}</span>
                      <span className="text-xs text-muted-foreground">{acc.email}</span>
                    </div>
                    <span className="text-xs uppercase tracking-wider text-muted-foreground">
                      {acc.role}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}