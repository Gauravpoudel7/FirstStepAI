import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const valid = password.length >= 8 && password === confirm && token.length > 0;

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!valid) return;
    setLoading(true);
    try {
      await api.post("/api/v1/reset-password", { token, new_password: password });
      toast.success("Password reset — please sign in");
      navigate("/login", { replace: true });
    } catch (err: any) {
      toast.error(err?.response?.data?.detail ?? "Could not reset password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-background px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="glass-strong w-full max-w-md rounded-2xl p-8"
      >
        <Link
          to="/login"
          className="text-xs text-muted-foreground hover:text-foreground"
        >
          ← Back to sign in
        </Link>
        <h1 className="mt-4 text-2xl font-semibold">Set a new password</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose a strong password (at least 8 characters).
        </p>

        {!token && (
          <div className="mt-6 rounded-lg border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
            Missing or invalid reset token. Request a new link from the
            forgot-password page.
          </div>
        )}

        {token && (
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div className="space-y-1">
              <Label htmlFor="pwd">New password</Label>
              <Input
                id="pwd"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="conf">Confirm new password</Label>
              <Input
                id="conf"
                type="password"
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                minLength={8}
              />
            </div>
            {password && confirm && password !== confirm && (
              <p className="text-xs text-rose-400">Passwords do not match.</p>
            )}
            <Button type="submit" className="w-full" disabled={!valid || loading}>
              {loading ? "Saving…" : "Reset password"}
            </Button>
          </form>
        )}
      </motion.div>
    </div>
  );
}