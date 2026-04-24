"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { fetchApi } from "./api";

interface AuthState {
  isAuthenticated: boolean;
  email: string | null;
  loading: boolean;
}

interface AuthContextType extends AuthState {
  login: (email: string) => Promise<string>;
  verify: (token: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    email: null,
    loading: true,
  });

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem("forge_access_token");
    const email = localStorage.getItem("forge_email");
    if (token && email) {
      setState({ isAuthenticated: true, email, loading: false });
    } else {
      setState((s) => ({ ...s, loading: false }));
    }
  }, []);

  const login = useCallback(async (email: string): Promise<string> => {
    const res = await fetchApi<{ message: string }>("/auth/magic-link", {
      method: "POST",
      body: JSON.stringify({ email }),
    });
    return res.message;
  }, []);

  const verify = useCallback(async (token: string): Promise<boolean> => {
    try {
      const res = await fetchApi<{
        access_token: string;
        refresh_token: string;
      }>("/auth/verify", {
        method: "POST",
        body: JSON.stringify({ token }),
      });
      localStorage.setItem("forge_access_token", res.access_token);
      localStorage.setItem("forge_refresh_token", res.refresh_token);
      // Decode email from JWT payload
      const payload = JSON.parse(atob(res.access_token.split(".")[1]));
      localStorage.setItem("forge_email", payload.sub);
      setState({ isAuthenticated: true, email: payload.sub, loading: false });
      return true;
    } catch {
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("forge_access_token");
    localStorage.removeItem("forge_refresh_token");
    localStorage.removeItem("forge_email");
    setState({ isAuthenticated: false, email: null, loading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, verify, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
