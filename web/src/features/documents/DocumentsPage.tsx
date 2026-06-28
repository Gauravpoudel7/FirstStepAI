import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  FileText,
  Filter,
  Loader2,
  RefreshCw,
  Trash2,
  Upload,
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
import { useAuthStore } from "@/store/auth.store";
import type { DocumentOut } from "@/lib/types";

const ROLES = ["all", "employee", "manager", "hr", "admin"] as const;

export default function DocumentsPage() {
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === "admin";
  const qc = useQueryClient();
  const [filter, setFilter] = useState<string>("all");
  const [showUpload, setShowUpload] = useState(false);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [docType, setDocType] = useState("policy");
  const [department, setDepartment] = useState("HR");
  const [requiredRole, setRequiredRole] = useState("all");

  const { data: docs, isLoading } = useQuery<DocumentOut[]>({
    queryKey: ["documents"],
    queryFn: async () => (await api.get("/api/v1/documents")).data,
  });

  const uploadMut = useMutation({
    mutationFn: async () =>
      (
        await api.post("/api/v1/documents", {
          title,
          text,
          doc_type: docType,
          department,
          required_role: requiredRole,
        })
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document uploaded and indexed");
      setTitle("");
      setText("");
      setShowUpload(false);
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Upload failed"),
  });

  const deleteMut = useMutation({
    mutationFn: async (id: string) => api.delete(`/api/v1/documents/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document deleted");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Delete failed"),
  });

  const reindexMut = useMutation({
    mutationFn: async () =>
      (await api.post("/api/v1/documents/reindex")).data,
    onSuccess: (d: any) =>
      toast.success(`Reindexed ${d?.chunks ?? 0} chunks from bundled PDF`),
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Reindex failed"),
  });

  const filtered = (docs ?? []).filter(
    (d) => filter === "all" || d.required_role === filter,
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold">Documents</h1>
          <p className="text-sm text-muted-foreground">
            Browse and (admin-only) manage the knowledge base.
          </p>
        </div>
        {isAdmin && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => reindexMut.mutate()}
              disabled={reindexMut.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              {reindexMut.isPending ? "Reindexing…" : "Reindex all"}
            </Button>
            <Button onClick={() => setShowUpload((v) => !v)}>
              <Upload className="mr-2 h-4 w-4" />
              {showUpload ? "Close" : "Upload"}
            </Button>
          </div>
        )}
      </div>

      {isAdmin && showUpload && (
        <Card>
          <CardHeader>
            <CardTitle>Upload document</CardTitle>
            <CardDescription>
              Paste plain text. The server chunks and embeds it.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                uploadMut.mutate();
              }}
              className="space-y-4"
            >
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1">
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="docType">Doc type</Label>
                  <select
                    id="docType"
                    value={docType}
                    onChange={(e) => setDocType(e.target.value)}
                    className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm"
                  >
                    <option value="policy">Policy</option>
                    <option value="handbook">Handbook</option>
                    <option value="memo">Memo</option>
                    <option value="form">Form</option>
                  </select>
                </div>
                <div className="space-y-1">
                  <Label htmlFor="dept">Department</Label>
                  <Input
                    id="dept"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="role">Visible to</Label>
                  <select
                    id="role"
                    value={requiredRole}
                    onChange={(e) => setRequiredRole(e.target.value)}
                    className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm"
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r === "all" ? "Everyone" : r}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="space-y-1">
                <Label htmlFor="text">Content</Label>
                <textarea
                  id="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={6}
                  required
                  className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm font-mono"
                  placeholder="Paste document text here…"
                />
              </div>
              <Button type="submit" disabled={uploadMut.isPending}>
                {uploadMut.isPending ? "Uploading…" : "Upload + index"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-4 w-4" /> All documents
              </CardTitle>
              <CardDescription>
                {filtered.length} of {docs?.length ?? 0} visible
              </CardDescription>
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="rounded-md border border-border bg-secondary/40 px-3 py-1 text-sm"
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r === "all" ? "All roles" : `Role: ${r}`}
                </option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading…
            </div>
          ) : !filtered.length ? (
            <p className="text-sm text-muted-foreground">No documents match.</p>
          ) : (
            <ul className="divide-y divide-border">
              {filtered.map((d) => (
                <li
                  key={d.id}
                  className="flex items-center justify-between gap-3 py-3"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <div className="truncate font-medium">{d.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {d.doc_type} • {d.department} • role: {d.required_role} •{" "}
                        {d.chunk_count} chunks
                      </div>
                    </div>
                  </div>
                  {isAdmin && (
                    <button
                      type="button"
                      onClick={() => deleteMut.mutate(d.id)}
                      className="rounded-md p-1 text-muted-foreground hover:bg-rose-500/20 hover:text-rose-300"
                      aria-label={`Delete ${d.title}`}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}