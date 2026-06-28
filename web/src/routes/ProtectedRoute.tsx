import { type ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "@/store/auth.store";
import { useMe } from "@/hooks/use-auth";
import { Loader2 } from "lucide-react";

export function ProtectedRoute({
  children,
  requiredRole,
}: {
  children: ReactNode;
  requiredRole?: string | string[];
}) {
  const user = useAuthStore((s) => s.user);
  const location = useLocation();
  const { isLoading, isError } = useMe();

  // No cached user and /auth/me failed → bounce to login.
  if (!user && (isError || !isLoading)) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // First boot — fetch /me. Show a spinner so we don't flash the login page
  // on every refresh.
  if (!user) {
    return (
      <div className="grid h-screen w-screen place-items-center bg-background">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (requiredRole) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    if (!roles.includes(user.role)) {
      return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
}