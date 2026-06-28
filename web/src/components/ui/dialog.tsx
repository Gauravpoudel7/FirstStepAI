import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface DialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

interface DialogTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

interface DialogDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            onClick={() => onOpenChange(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />
          <div className="relative z-10 max-h-[90vh] w-full max-w-lg overflow-y-auto p-4">
            {children}
          </div>
        </div>
      )}
    </AnimatePresence>
  );
}

export function DialogContent({ children, className, ...rest }: DialogContentProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 8 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 8 }}
      transition={{ duration: 0.18 }}
      className={cn(
        "relative rounded-2xl border border-border bg-card p-6 shadow-2xl",
        className,
      )}
    >
      {children}
    </motion.div>
  );
}

export function DialogHeader({ children, className, ...rest }: DialogHeaderProps) {
  return (
    <div className={cn("mb-4 space-y-1", className)} {...rest}>
      {children}
    </div>
  );
}

export function DialogFooter({ children, className, ...rest }: DialogFooterProps) {
  return (
    <div
      className={cn("mt-6 flex justify-end gap-2", className)}
      {...rest}
    >
      {children}
    </div>
  );
}

export function DialogTitle({ children, className, ...rest }: DialogTitleProps) {
  return (
    <h2
      className={cn("text-lg font-semibold", className)}
      {...rest}
    >
      {children}
    </h2>
  );
}

export function DialogDescription({
  children,
  className,
  ...rest
}: DialogDescriptionProps) {
  return (
    <p
      className={cn("text-sm text-muted-foreground", className)}
      {...rest}
    >
      {children}
    </p>
  );
}

export function DialogCloseButton({ onClose }: { onClose: () => void }) {
  return (
    <button
      type="button"
      onClick={onClose}
      aria-label="Close"
      className="absolute right-3 top-3 rounded-md p-1 text-muted-foreground hover:bg-secondary hover:text-foreground"
    >
      <X className="h-4 w-4" />
    </button>
  );
}