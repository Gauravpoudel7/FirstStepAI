import { motion } from "framer-motion";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  title: string;
  description?: string;
  badge?: string;
  children?: React.ReactNode;
}

export function PlaceholderPage({ title, description, badge, children }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-2xl font-semibold">{title}</h1>
        {description && <p className="text-muted-foreground">{description}</p>}
      </div>
      <Card className="glass">
        <CardHeader>
          <CardTitle>{badge ?? "Coming in a later phase"}</CardTitle>
          <CardDescription>
            This page is part of the migration roadmap. Backend endpoints are
            scaffolded in the FastAPI service and will be wired up in subsequent
            phases.
          </CardDescription>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </motion.div>
  );
}