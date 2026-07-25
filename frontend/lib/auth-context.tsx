"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("ezoo_token");
    if (stored) {
      setToken(stored);
      fetchUser(stored);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (tok: string) => {
    try {
      const res = await fetch("/api/auth/me", {
        headers: { Authorization: `Bearer ${tok}` },
      });
      if (res.ok) {
        setUser(await res.json());
      } else {
        localStorage.removeItem("ezoo_token");
        setToken(null);
        setUser(null);
      }
    } catch {
      localStorage.removeItem("ezoo_token");
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Login failed");
    }
    const data = await res.json();
    localStorage.setItem("ezoo_token", data.access_token);
    setToken(data.access_token);
    await fetchUser(data.access_token);
  };

  const logout = useCallback(() => {
    localStorage.removeItem("ezoo_token");
    setToken(null);
    setUser(null);
    window.location.href = "/login";
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
