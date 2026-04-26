import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthState } from '@/types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useAuth = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        try {
          const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
          });
          if (!res.ok) return false;
          const data = await res.json();
          set({
            user: { username: data.username },
            token: data.access_token,
            isAuthenticated: true,
          });
          return true;
        } catch {
          return false;
        }
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'congroup-auth',
    }
  )
);
