import { Outlet, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Menu } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { useSidebar } from '@/hooks/useSidebar';

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/': {
    title: 'Resumen de Vendedores',
    subtitle: 'Grupo Cars Mazda — Análisis operativo del equipo de ventas',
  },
  '/balance': {
    title: 'Balance P&G',
    subtitle: 'Análisis contable — Pérdidas y Ganancias',
  },
};

export function Layout() {
  const { collapsed, setMobileOpen } = useSidebar();
  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: '', subtitle: '' };

  return (
    <div className="min-h-screen bg-[#F1F5F9]">
      <Sidebar />

      {/* Main Content */}
      <main
        className="transition-all duration-350 ease-out min-h-screen lg:ml-0"
        style={{
          marginLeft: undefined, // Let Tailwind handle mobile (ml-0 above)
          transitionTimingFunction: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          ['--sidebar-width' as string]: collapsed ? '76px' : '268px',
        }}
      >
        {/* We use a style tag for dynamic desktop margin since Tailwind can't do runtime values */}
        <style>{`
          @media (min-width: 1024px) {
            main { margin-left: ${collapsed ? '76px' : '268px'} !important; }
          }
        `}</style>

        {/* Top Header */}
        <motion.header
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky top-0 z-40 bg-white border-b border-slate-200/60 shadow-sm"
        >
          <div className="flex items-center justify-between px-4 md:px-6 py-3 md:py-4">
            <div className="flex items-center gap-3">
              {/* Mobile hamburger */}
              <button
                onClick={() => setMobileOpen(true)}
                className="lg:hidden p-2 -ml-2 rounded-lg text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div>
                <motion.h1
                  key={pageInfo.title}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-lg md:text-xl font-bold text-slate-800 tracking-tight"
                >
                  {pageInfo.title}
                </motion.h1>
                <motion.p
                  key={pageInfo.subtitle}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.05 }}
                  className="text-[11px] md:text-xs text-slate-400 mt-0.5 font-medium"
                >
                  {pageInfo.subtitle}
                </motion.p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-[11px] font-semibold text-emerald-700">Sistema en línea</span>
              </div>
            </div>
          </div>
        </motion.header>

        {/* Page Content */}
        <div className="p-4 md:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
