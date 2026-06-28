import { cn } from "@/lib/utils";

interface RoleBadgeProps {
  role: string;
  className?: string;
}

const COLOR: Record<string, string> = {
  admin: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  hr: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  manager: "bg-blue-500/15 text-blue-300 border-blue-500/30",
  employee: "bg-violet-500/15 text-violet-300 border-violet-500/30",
};

export function RoleBadge({ role, className }: RoleBadgeProps) {
  const styles = COLOR[role] ?? "bg-secondary text-secondary-foreground border-border";
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium uppercase tracking-wider",
        styles,
        className,
      )}
    >
      {role}
    </span>
  );
}