import React, { createContext, useContext, useMemo, useState } from "react";

type User = { id: number; email: string; role: string; full_name?: string };

const AuthCtx = createContext<{
  user: User | null;
  setUser: (u: User | null) => void;
  token: string | null;
  setToken: (t: string | null) => void;
} | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setTokenState] = useState<string | null>(localStorage.getItem("token"));
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  const setToken = (t: string | null) => {
    setTokenState(t);
    if (t) localStorage.setItem("token", t);
    else localStorage.removeItem("token");
  };

  const setUserPersist = (u: User | null) => {
    setUser(u);
    if (u) localStorage.setItem("user", JSON.stringify(u));
    else localStorage.removeItem("user");
  };

  const v = useMemo(
    () => ({ user, setUser: setUserPersist, token, setToken }),
    [user, token]
  );

  return <AuthCtx.Provider value={v}>{children}</AuthCtx.Provider>;
}

export function useAuth() {
  const x = useContext(AuthCtx);
  if (!x) throw new Error("AuthProvider missing");
  return x;
}
