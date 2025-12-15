import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type Theme = 'light' | 'dark';

export interface GlobalState {
  theme: Theme;
  isLoading: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useGlobalStore = create<GlobalState>()(
  persist(
    (set) => ({
      theme: 'light',
      isLoading: false,
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({
        theme: state.theme === 'light' ? 'dark' : 'light'
      })),
      setLoading: (isLoading) => set({ isLoading })
    }),
    {
      name: 'global-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
