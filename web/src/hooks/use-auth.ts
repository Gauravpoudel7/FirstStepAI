import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth.store";

export function useMe() {
  const setUser = useAuthStore((s) => s.setUser);
  return useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      const { data } = await api.get("/api/v1/auth/me");
      setUser(data);
      return data;
    },
    retry: false,
    staleTime: 60_000,
  });
}

export function useLogin() {
  const qc = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);
  return async (email: string, password: string, rememberMe = false) => {
    const { data } = await api.post("/api/v1/auth/login", {
      email,
      password,
      remember_me: rememberMe,
    });
    setUser(data.user);
    await qc.invalidateQueries();
    return data.user;
  };
}

export function useLogout() {
  const qc = useQueryClient();
  const logout = useAuthStore((s) => s.logout);
  return async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } catch {
      // best-effort — even if the server call fails we still clear local state
    }
    logout();
    qc.clear();
  };
}