import { useState } from "react";
import { motion } from "framer-motion";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth.store";
import { api } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { initials } from "@/lib/utils";
import { RoleBadge } from "@/components/layout/RoleBadge";

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const queryClient = useQueryClient();
  const [changePwdOpen, setChangePwdOpen] = useState(false);

  if (!user) return null;
  const profile = (user.employee_profile ?? {}) as Record<string, any>;

  const saveMutation = useMutation({
    mutationFn: async (patch: Record<string, any>) => {
      const { data } = await api.patch("/api/v1/profile/me", patch);
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["me"] });
      toast.success("Profile updated");
      if (data?.full_name) {
        setUser({ ...user, full_name: data.full_name });
      }
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail ?? "Could not save profile");
    },
  });

  const changePwdMutation = useMutation({
    mutationFn: async (body: {
      current_password: string;
      new_password: string;
    }) => {
      const { data } = await api.post("/api/v1/change-password", body);
      return data;
    },
    onSuccess: () => {
      toast.success("Password changed");
      setChangePwdOpen(false);
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail ?? "Could not change password");
    },
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">My Profile</h1>
        <Button variant="outline" onClick={() => setChangePwdOpen(true)}>
          Change password
        </Button>
      </div>

      <Card className="glass">
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="grid h-16 w-16 place-items-center rounded-2xl bg-brand-gradient text-white text-2xl font-semibold shadow-soft">
              {initials(user.full_name)}
            </div>
            <div>
              <CardTitle>{user.full_name}</CardTitle>
              <CardDescription>{user.email}</CardDescription>
              <div className="mt-2">
                <RoleBadge role={user.role} />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <Field label="Employee ID" value={profile.employee_id} />
          <Field label="Designation" value={profile.designation} />
          <Field label="Department" value={profile.department} />
          <Field label="Office Location" value={profile.office_location} />
          <Field label="Manager" value={profile.manager_name} />
          <Field
            label="Leave Balance"
            value={
              profile.leave_balance != null
                ? `${profile.leave_balance} days`
                : "—"
            }
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Active Projects</CardTitle>
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

      {changePwdOpen && (
        <ChangePasswordDialog
          onClose={() => setChangePwdOpen(false)}
          onSubmit={(body) => changePwdMutation.mutate(body)}
          loading={changePwdMutation.isPending}
        />
      )}
    </motion.div>
  );
}

function Field({ label, value }: { label: string; value?: string | number }) {
  return (
    <div className="rounded-lg border border-border bg-secondary/40 px-3 py-2">
      <div className="text-xs uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className="font-medium">{value ?? "—"}</div>
    </div>
  );
}

function ChangePasswordDialog({
  onClose,
  onSubmit,
  loading,
}: {
  onClose: () => void;
  onSubmit: (body: { current_password: string; new_password: string }) => void;
  loading: boolean;
}) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const valid = current.length > 0 && next.length >= 8 && next === confirm;

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="glass-strong w-full max-w-md rounded-2xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold">Change password</h2>
        <p className="text-sm text-muted-foreground">
          Enter your current password and a new password of at least 8
          characters.
        </p>
        <form
          className="mt-4 space-y-3"
          onSubmit={(e) => {
            e.preventDefault();
            if (valid) onSubmit({ current_password: current, new_password: next });
          }}
        >
          <div className="space-y-1">
            <Label htmlFor="cur">Current password</Label>
            <Input
              id="cur"
              type="password"
              autoComplete="current-password"
              value={current}
              onChange={(e) => setCurrent(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="new">New password</Label>
            <Input
              id="new"
              type="password"
              autoComplete="new-password"
              value={next}
              onChange={(e) => setNext(e.target.value)}
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
          {next && confirm && next !== confirm && (
            <p className="text-xs text-rose-400">Passwords do not match.</p>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={!valid || loading}>
              {loading ? "Saving…" : "Update password"}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
