import { create } from 'zustand';

interface SidebarState {
  collapsed: boolean;
  mobileOpen: boolean;
  toggle: () => void;
  setCollapsed: (v: boolean) => void;
  setMobileOpen: (v: boolean) => void;
}

const saved = localStorage.getItem('sidebar-collapsed');

export const useSidebar = create<SidebarState>((set) => ({
  collapsed: saved ? saved === 'true' : false,
  mobileOpen: false,
  toggle: () => set((state) => {
    const next = !state.collapsed;
    localStorage.setItem('sidebar-collapsed', String(next));
    return { collapsed: next };
  }),
  setCollapsed: (v) => {
    localStorage.setItem('sidebar-collapsed', String(v));
    set({ collapsed: v });
  },
  setMobileOpen: (v) => set({ mobileOpen: v }),
}));
