import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Trash2, RefreshCw, Upload, FileText } from "lucide-react";
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
import type { DocumentOut } from "@/lib/types";

export default function AdminPage() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [docType, setDocType] = useState("policy");
  const [department, setDepartment] = useState("HR");
  const [requiredRole, setRequiredRole] = useState("all");

  const { data: docs } = useQuery<DocumentOut[]>({
    queryKey: ["documents"],
    queryFn: async () => (await api.get("/api/v1/documents")).data,
  });

  const uploadMutation = useMutation({
    mutationFn: async (body: {
      title: string;
      text: string;
      doc_type: string;
      department: string;
      required_role: string;
    }) => (await api.post("/api/v1/documents", body)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document uploaded and indexed");
      setTitle("");
      setText("");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Upload failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => api.delete(`/api/v1/documents/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      toast.success("Document deleted");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Delete failed"),
  });

  const reindexMutation = useMutation({
    mutationFn: async () => (await api.post("/api/v1/documents/reindex")).data,
    onSuccess: (data) =>
      toast.success(`Reindexed ${data.chunks ?? 0} chunks from bundled PDF`),
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Reindex failed"),
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Admin Console</h1>
          <p className="text-sm text-muted-foreground">
            Manage documents and re-index the knowledge base.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => reindexMutation.mutate()}
          disabled={reindexMutation.isPending}
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          {reindexMutation.isPending ? "Reindexing…" : "Reindex all"}
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Upload document</CardTitle>
            <CardDescription>
              Paste plain text. The server chunks and embeds it, then tags with
              the role below.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                uploadMutation.mutate({
                  title,
                  text,
                  doc_type: docType,
                  department,
                  required_role: requiredRole,
                });
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
                  <Label htmlFor="type">Doc type</Label>
                  <select
                    id="type"
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
                    <option value="all">Everyone</option>
                    <option value="employee">Employees</option>
                    <option value="manager">Managers</option>
                    <option value="hr">HR</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              </div>
              <div className="space-y-1">
                <Label htmlFor="text">Text content</Label>
                <textarea
                  id="text"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={8}
                  required
                  className="w-full rounded-md border border-border bg-secondary/40 px-3 py-2 text-sm font-mono"
                  placeholder="Paste the document text here…"
                />
              </div>
              <Button type="submit" disabled={uploadMutation.isPending}>
                <Upload className="mr-2 h-4 w-4" />
                {uploadMutation.isPending ? "Uploading…" : "Upload + index"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Documents</CardTitle>
            <CardDescription>
              {docs?.length ?? 0} in the knowledge base
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 max-h-[28rem] overflow-y-auto">
            {docs?.length ? (
              docs.map((d) => (
                <div
                  key={d.id}
                  className="flex items-center justify-between rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <div className="min-w-0">
                      <div className="truncate font-medium">{d.title}</div>
                      <div className="text-xs text-muted-foreground">
                        {d.required_role} • {d.chunk_count} chunks
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    className="ml-2 rounded-md p-1 text-muted-foreground hover:bg-rose-500/20 hover:text-rose-300"
                    onClick={() => deleteMutation.mutate(d.id)}
                    aria-label={`Delete ${d.title}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No documents yet.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}