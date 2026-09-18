import { create } from "zustand";

import { api, clearToken, getToken, setToken } from "@/lib/api";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  loading: boolean;
  loadMe: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshCredits: () => Promise<void>;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,
  loadMe: async () => {
    if (!getToken()) {
      set({ user: null, loading: false });
      return;
    }
    try {
      const user = await api<User>("/auth/me");
      set({ user, loading: false });
    } catch {
      clearToken();
      set({ user: null, loading: false });
    }
  },
  login: async (email, password) => {
    const { access_token } = await api<{ access_token: string }>("/auth/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
    setToken(access_token);
    const user = await api<User>("/auth/me");
    set({ user });
  },
  register: async (email, password, fullName) => {
    const { access_token } = await api<{ access_token: string }>("/auth/register", {
      method: "POST",
      auth: false,
      body: { email, password, full_name: fullName },
    });
    setToken(access_token);
    const user = await api<User>("/auth/me");
    set({ user });
  },
  logout: () => {
    clearToken();
    set({ user: null });
  },
  refreshCredits: async () => {
    try {
      const user = await api<User>("/auth/me");
      set({ user });
    } catch {
      /* ignore */
    }
  },
}));
