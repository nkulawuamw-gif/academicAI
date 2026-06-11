import { create } from 'zustand';
import { User } from '@/types';
import { getStoredUser, setStoredUser } from '@/lib/auth';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setIsLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: getStoredUser(),
  isLoading: false,
  setUser: (user) => {
    setStoredUser(user!);
    set({ user });
  },
  setIsLoading: (isLoading) => set({ isLoading }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    set({ user: null });
  },
}));
