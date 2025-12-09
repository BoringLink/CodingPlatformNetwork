import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

interface UIState {
  // Theme
  theme: "light" | "dark" | "system";
  
  // Sidebar
  isSidebarOpen: boolean;
  
  // Filter panel
  isFilterPanelOpen: boolean;
  
  // Loading states
  isLoading: boolean;
  loadingMessage: string;
  
  // Actions
  setTheme: (theme: "light" | "dark" | "system") => void;
  toggleSidebar: () => void;
  setSidebarOpen: (isOpen: boolean) => void;
  toggleFilterPanel: () => void;
  setFilterPanelOpen: (isOpen: boolean) => void;
  setLoading: (isLoading: boolean, message?: string) => void;
}

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        theme: "system",
        isSidebarOpen: true,
        isFilterPanelOpen: false,
        isLoading: false,
        loadingMessage: "",

        // Actions
        setTheme: (theme) => set({ theme }),
        toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
        setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
        toggleFilterPanel: () =>
          set((state) => ({ isFilterPanelOpen: !state.isFilterPanelOpen })),
        setFilterPanelOpen: (isOpen) => set({ isFilterPanelOpen: isOpen }),
        setLoading: (isLoading, message = "") =>
          set({ isLoading, loadingMessage: message }),
      }),
      {
        name: "ui-storage",
      }
    ),
    { name: "UIStore" }
  )
);
