import { useQuery } from "@tanstack/react-query";
import { FileText, ShieldCheck, Tag, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { DocumentOut } from "@/lib/types";

const ROLE_LABEL: Record<string, string> = {
  all: "Everyone",
  employee: "Employees",
  manager: "Managers",
  hr: "HR",
  admin: "Admin",
};

const TYPE_LABEL: Record<string, string> = {
  policy: "Policy",
  handbook: "Handbook",
  memo: "Memo",
  form: "Form",
};

export default function KnowledgeBasePage() {
  const { data: docs, isLoading } = useQuery<DocumentOut[]>({
    queryKey: ["documents"],
    queryFn: async () => (await api.get("/api/v1/documents")).data,
    staleTime: 60_000,
  });

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-semibold">Knowledge Base</h1>
        <p className="text-sm text-muted-foreground">
          Documents available for your role.
        </p>
      </div>

      {isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Card key={i} className="glass animate-pulse">
              <CardHeader className="h-20" />
              <CardContent className="h-12" />
            </Card>
          ))}
        </div>
      )}

      {docs && docs.length === 0 && (
        <Card className="glass">
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            No documents available for your role yet.
          </CardContent>
        </Card>
      )}

      {docs && docs.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {docs.map((d) => (
            <Card key={d.id} className="glass hover:shadow-soft transition-shadow">
              <CardHeader>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <FileText className="h-4 w-4" />
                  <CardDescription>
                    {TYPE_LABEL[d.doc_type] ?? d.doc_type} • {d.department}
                  </CardDescription>
                </div>
                <CardTitle className="text-lg">{d.title}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  Visible to: {ROLE_LABEL[d.required_role] ?? d.required_role}
                </div>
                <div className="flex items-center gap-2">
                  <Tag className="h-3.5 w-3.5" />
                  {d.chunk_count} chunks indexed
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && !docs?.length && (
        <div className="hidden">
          <Loader2 />
        </div>
      )}
    </motion.div>
  );
}