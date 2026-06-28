import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Trash2,
  Pencil,
  MessageSquare,
  Check,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ConversationOut } from "@/lib/types";

export default function ChatHistoryPage() {
  const queryClient = useQueryClient();
  const [q, setQ] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState("");

  const { data: conversations = [], isLoading } = useQuery<ConversationOut[]>({
    queryKey: ["conversations", q],
    queryFn: async () =>
      (await api.get("/api/v1/conversations", { params: q ? { q } : {} })).data,
  });

  const renameMutation = useMutation({
    mutationFn: async (vars: { id: string; title: string }) =>
      (await api.patch(`/api/v1/conversations/${vars.id}`, { title: vars.title })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      toast.success("Renamed");
      setEditingId(null);
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Rename failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => api.delete(`/api/v1/conversations/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
      toast.success("Deleted");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Delete failed"),
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Chat History</h1>
          <p className="text-sm text-muted-foreground">
            Search, rename, or delete your past conversations.
          </p>
        </div>
        <div className="relative w-full max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search by title or preview…"
            className="pl-9"
          />
        </div>
      </div>

      <Card className="glass">
        <CardHeader>
          <CardTitle>Conversations</CardTitle>
          <CardDescription>
            {isLoading ? "Loading…" : `${conversations.length} conversation${conversations.length === 1 ? "" : "s"}`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {!isLoading && conversations.length === 0 && (
            <p className="py-8 text-center text-sm text-muted-foreground">
              No conversations yet. Start a new chat on the AI Chat page.
            </p>
          )}

          <AnimatePresence>
            {conversations.map((c) => (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20, height: 0 }}
                layout
                className="flex items-start gap-3 rounded-xl border border-border bg-secondary/40 px-4 py-3"
              >
                <MessageSquare className="mt-1 h-4 w-4 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  {editingId === c.id ? (
                    <form
                      onSubmit={(e) => {
                        e.preventDefault();
                        if (draftTitle.trim()) {
                          renameMutation.mutate({
                            id: c.id,
                            title: draftTitle.trim(),
                          });
                        }
                      }}
                      className="flex items-center gap-2"
                    >
                      <Input
                        autoFocus
                        value={draftTitle}
                        onChange={(e) => setDraftTitle(e.target.value)}
                      />
                      <Button
                        type="submit"
                        size="sm"
                        variant="outline"
                        disabled={renameMutation.isPending}
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingId(null)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </form>
                  ) : (
                    <>
                      <div className="truncate font-medium">{c.title}</div>
                      {c.preview && (
                        <div className="mt-0.5 truncate text-xs text-muted-foreground">
                          {c.preview}…
                        </div>
                      )}
                      <div className="mt-1 text-xs text-muted-foreground">
                        Updated {new Date(c.updated_at).toLocaleString()}
                      </div>
                    </>
                  )}
                </div>
                {editingId !== c.id && (
                  <div className="flex shrink-0 gap-1">
                    <button
                      type="button"
                      className="rounded-md p-2 text-muted-foreground hover:bg-secondary hover:text-foreground"
                      onClick={() => {
                        setEditingId(c.id);
                        setDraftTitle(c.title);
                      }}
                      aria-label="Rename"
                    >
                      <Pencil className="h-4 w-4" />
                    </button>
                    <button
                      type="button"
                      className="rounded-md p-2 text-muted-foreground hover:bg-rose-500/20 hover:text-rose-300"
                      onClick={() => {
                        if (confirm(`Delete "${c.title}"?`)) {
                          deleteMutation.mutate(c.id);
                        }
                      }}
                      aria-label="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  );
}