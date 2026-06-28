import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Briefcase,
  CalendarDays,
  Loader2,
  Pencil,
  Plus,
  Trash2,
  Users,
} from "lucide-react";
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuthStore } from "@/store/auth.store";
import type { ProjectOut, ProjectEmployeeOption } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  active: "bg-emerald-500/15 text-emerald-300",
  paused: "bg-amber-500/15 text-amber-300",
  completed: "bg-blue-500/15 text-blue-300",
  archived: "bg-zinc-500/15 text-zinc-300",
};

export default function ProjectsPage() {
  const user = useAuthStore((s) => s.user);
  const qc = useQueryClient();
  const canCreate = user?.role === "manager" || user?.role === "admin";
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<ProjectOut | null>(null);
  const [form, setForm] = useState({
    name: "",
    description: "",
    status: "active",
    tags: "",
    member_ids: [] as string[],
  });

  const { data: projects, isLoading } = useQuery<ProjectOut[]>({
    queryKey: ["projects"],
    queryFn: async () => (await api.get("/api/v1/projects")).data,
  });

  const { data: roster } = useQuery<ProjectEmployeeOption[]>({
    queryKey: ["projects", "roster"],
    queryFn: async () =>
      (await api.get("/api/v1/projects/employees/options")).data,
    enabled: canCreate,
  });

  const createMut = useMutation({
    mutationFn: async (body: typeof form) =>
      (
        await api.post("/api/v1/projects", {
          name: body.name,
          description: body.description,
          status: body.status,
          tags: body.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          member_ids: body.member_ids,
        })
      ).data as ProjectOut,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project created");
      setOpen(false);
      resetForm();
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Could not create project"),
  });

  const updateMut = useMutation({
    mutationFn: async (vars: { id: string; body: { name?: string; description?: string; status?: string; tags?: string[] } }) =>
      (
        await api.patch(`/api/v1/projects/${vars.id}`, vars.body)
      ).data as ProjectOut,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project updated");
      setEditing(null);
      resetForm();
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Update failed"),
  });

  const deleteMut = useMutation({
    mutationFn: async (id: string) => api.delete(`/api/v1/projects/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["projects"] });
      toast.success("Project deleted");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Delete failed"),
  });

  function resetForm() {
    setForm({ name: "", description: "", status: "active", tags: "", member_ids: [] });
  }

  function openEdit(p: ProjectOut) {
    setEditing(p);
    setForm({
      name: p.name,
      description: p.description,
      status: p.status,
      tags: (p.tags || []).join(", "),
      member_ids: p.member_ids ?? [],
    });
  }

  function toggleMember(id: string) {
    setForm((f) => ({
      ...f,
      member_ids: f.member_ids.includes(id)
        ? f.member_ids.filter((x) => x !== id)
        : [...f.member_ids, id],
    }));
  }

  const grouped = useMemo(() => {
    const m = new Map<string, ProjectOut[]>();
    (projects ?? []).forEach((p) => {
      const list = m.get(p.status) ?? [];
      list.push(p);
      m.set(p.status, list);
    });
    return m;
  }, [projects]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold">Projects</h1>
          <p className="text-sm text-muted-foreground">
            {projects?.length ?? 0} project{(projects?.length ?? 0) === 1 ? "" : "s"}{" "}
            visible to you.
          </p>
        </div>
        {canCreate && (
          <Button
            onClick={() => {
              resetForm();
              setOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" /> New project
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading…
        </div>
      ) : !projects?.length ? (
        <Card>
          <CardHeader>
            <CardTitle>No projects yet</CardTitle>
            <CardDescription>
              {canCreate
                ? "Create your first project to get started."
                : "Projects you're added to will appear here."}
            </CardDescription>
          </CardHeader>
        </Card>
      ) : (
        ["active", "paused", "completed", "archived"]
          .filter((status) => grouped.get(status)?.length)
          .map((status) => (
            <section key={status} className="space-y-3">
              <h2 className="text-sm uppercase tracking-wider text-muted-foreground">
                {status}
              </h2>
              <div className="grid gap-4 md:grid-cols-2">
                {grouped.get(status)!.map((p) => (
                  <Card key={p.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <CardTitle className="flex items-center gap-2">
                            <Briefcase className="h-4 w-4 text-muted-foreground" />
                            {p.name}
                          </CardTitle>
                          <CardDescription className="line-clamp-2">
                            {p.description || "No description"}
                          </CardDescription>
                        </div>
                        <span
                          className={`shrink-0 rounded-full px-2 py-0.5 text-xs ${
                            STATUS_COLORS[p.status] ?? STATUS_COLORS.archived
                          }`}
                        >
                          {p.status}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
                        {(p.start_date || p.end_date) && (
                          <span className="inline-flex items-center gap-1">
                            <CalendarDays className="h-3 w-3" />
                            {p.start_date ?? "—"} → {p.end_date ?? "—"}
                          </span>
                        )}
                        <span className="inline-flex items-center gap-1">
                          <Users className="h-3 w-3" />
                          {p.member_ids?.length ?? 0} member
                          {(p.member_ids?.length ?? 0) === 1 ? "" : "s"}
                        </span>
                      </div>
                      {p.tags?.length ? (
                        <div className="flex flex-wrap gap-1">
                          {p.tags.map((t) => (
                            <span
                              key={t}
                              className="rounded-md bg-secondary px-2 py-0.5 text-xs"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      ) : null}
                      {(canCreate || user?.role === "admin") && (
                        <div className="flex gap-2 pt-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openEdit(p)}
                          >
                            <Pencil className="mr-2 h-3 w-3" /> Edit
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => deleteMut.mutate(p.id)}
                            disabled={deleteMut.isPending}
                          >
                            <Trash2 className="mr-2 h-3 w-3" /> Delete
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          ))
      )}

      {/* Create / edit dialog */}
      <Dialog
        open={open || !!editing}
        onOpenChange={(v) => {
          if (!v) {
            setOpen(false);
            setEditing(null);
            resetForm();
          }
        }}
      >
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit project" : "New project"}</DialogTitle>
            <DialogDescription>
              {editing
                ? "Update details. Only the owner or admin can edit."
                : "Owners can update and delete; add members to share visibility."}
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (editing) {
                updateMut.mutate({
                  id: editing.id,
                  body: {
                    name: form.name,
                    description: form.description,
                    status: form.status,
                    tags: form.tags
                      .split(",")
                      .map((t) => t.trim())
                      .filter(Boolean),
                  },
                });
              } else {
                createMut.mutate(form);
              }
            }}
            className="space-y-4"
          >
            <div className="space-y-1">
              <Label htmlFor="pname">Name</Label>
              <Input
                id="pname"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="pdesc">Description</Label>
              <textarea
                id="pdesc"
                rows={3}
                value={form.description}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm"
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <Label htmlFor="pstatus">Status</Label>
                <select
                  id="pstatus"
                  value={form.status}
                  onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm"
                >
                  <option value="active">Active</option>
                  <option value="paused">Paused</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
              <div className="space-y-1">
                <Label htmlFor="ptags">Tags (comma-separated)</Label>
                <Input
                  id="ptags"
                  value={form.tags}
                  onChange={(e) => setForm({ ...form, tags: e.target.value })}
                  placeholder="ai, onboarding"
                />
              </div>
            </div>
            {!editing && roster?.length ? (
              <div className="space-y-1">
                <Label>Members</Label>
                <div className="max-h-40 space-y-1 overflow-y-auto rounded-md border border-border bg-secondary/40 p-2">
                  {roster.map((r) => (
                    <label
                      key={r.id}
                      className="flex items-center justify-between rounded px-2 py-1 text-sm hover:bg-secondary"
                    >
                      <span>
                        {r.name}{" "}
                        <span className="text-xs text-muted-foreground">
                          ({r.employee_id} • {r.department})
                        </span>
                      </span>
                      <input
                        type="checkbox"
                        checked={form.member_ids.includes(r.id)}
                        onChange={() => toggleMember(r.id)}
                        className="h-4 w-4 accent-brand"
                      />
                    </label>
                  ))}
                </div>
              </div>
            ) : null}
            <DialogFooter>
              <Button
                type="submit"
                disabled={createMut.isPending || updateMut.isPending}
              >
                {editing
                  ? updateMut.isPending
                    ? "Saving…"
                    : "Save changes"
                  : createMut.isPending
                    ? "Creating…"
                    : "Create project"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </motion.div>
  );
}