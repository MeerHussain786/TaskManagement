import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserResponse } from '@/services/api/generated/models';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserResponse | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: UserResponse) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      setUser: (user) => set({ user }),
      logout: () => {
        set({ accessToken: null, refreshToken: null, user: null });
        if (typeof document !== 'undefined') {
          document.cookie = 'token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
