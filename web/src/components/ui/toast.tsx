import { createContext, useCallback, useContext, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

type ToastVariant = "success" | "error" | "info";
type Toast = { id: number; title: string; description?: string; variant: ToastVariant };

type ToastContextValue = {
  show: (t: Omit<Toast, "id">) => void;
};

const ToastContext = createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const show = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now() + Math.random();
    setToasts((cur) => [...cur, { ...t, id }]);
    setTimeout(() => {
      setToasts((cur) => cur.filter((x) => x.id !== id));
    }, 4000);
  }, []);

  return (
    <ToastContext.Provider value={{ show }}>
      {children}
      <div className="pointer-events-none fixed bottom-6 right-6 z-[60] flex w-80 flex-col gap-2">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 40 }}
              transition={{ duration: 0.25 }}
              className={
                "pointer-events-auto rounded-xl border px-4 py-3 shadow-soft backdrop-blur " +
                (t.variant === "success"
                  ? "border-emerald-400/30 bg-emerald-500/15 text-emerald-100"
                  : t.variant === "error"
                  ? "border-rose-400/30 bg-rose-500/15 text-rose-100"
                  : "border-white/10 bg-white/10 text-white")
              }
            >
              <div className="text-sm font-semibold">{t.title}</div>
              {t.description && (
                <div className="mt-1 text-xs opacity-80">{t.description}</div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    // Graceful fallback so un-mounted components don't crash.
    return { show: () => undefined };
  }
  return ctx;
}