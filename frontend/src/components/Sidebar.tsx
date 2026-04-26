import { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Table2,
  LogOut,
  ChevronLeft,
  ChevronRight,
  User,
  X,
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useSidebar } from '@/hooks/useSidebar';
import { cn } from '@/lib/utils';

const menuItems = [
  { path: '/', label: 'Resumen de Vendedores', icon: LayoutDashboard },
  { path: '/balance', label: 'Balance P&G', icon: Table2 },
];

export function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { collapsed, toggle, mobileOpen, setMobileOpen } = useSidebar();

  useEffect(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved) {
      useSidebar.getState().setCollapsed(saved === 'true');
    }
  }, []);

  // Close mobile sidebar on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname, setMobileOpen]);

  // Body scroll lock when mobile sidebar is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [mobileOpen]);

  const sidebarContent = (
    <>
      {/* Glass overlay */}
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 50% at 20% 40%, rgba(46,107,230,0.15) 0%, transparent 70%)',
        }}
      />

      {/* Logo Section */}
      <div className="relative z-10 flex items-center justify-center h-[72px] px-4 border-b border-white/5">
        <AnimatePresence mode="wait">
          {!collapsed ? (
            <motion.div
              key="logo-full"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.25 }}
              className="flex items-center gap-3"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#2E6BE6] to-[#1B3A6B] flex items-center justify-center shadow-lg shadow-blue-900/30">
                <span className="text-white font-bold text-sm tracking-tight">CG</span>
              </div>
              <div className="flex flex-col">
                <span className="text-white font-bold text-[15px] tracking-tight leading-tight">
                  Congroup
                </span>
                <span className="text-[10px] font-medium text-blue-300/60 tracking-widest uppercase">
                  Analytics
                </span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="logo-mini"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.25 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#2E6BE6] to-[#1B3A6B] flex items-center justify-center shadow-lg shadow-blue-900/30"
            >
              <span className="text-white font-bold text-sm">CG</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex-1 px-3 pt-5 space-y-1.5 overflow-y-auto overscroll-contain">
        <AnimatePresence>
          {!collapsed && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="px-3 mb-3 text-[10px] font-semibold text-blue-300/40 uppercase tracking-[2px]"
            >
              Principal
            </motion.p>
          )}
        </AnimatePresence>

        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'group relative flex items-center rounded-xl transition-all duration-300 ease-out',
                isActive
                  ? 'bg-gradient-to-r from-blue-600/20 to-blue-500/5 text-white'
                  : 'text-blue-200/50 hover:text-blue-100 hover:bg-white/[0.03]',
                collapsed ? 'justify-center px-0 py-3' : 'px-3.5 py-2.5'
              )}
            >
              {/* Active indicator glow */}
              {isActive && (
                <motion.div
                  layoutId="active-pill"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-6 rounded-full bg-gradient-to-b from-[#5DADE2] to-[#2E6BE6]"
                  style={{ boxShadow: '0 0 12px rgba(93,173,226,0.5)' }}
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}

              {/* Icon */}
              <div
                className={cn(
                  'relative flex items-center justify-center rounded-lg transition-all duration-300',
                  isActive
                    ? 'text-white'
                    : 'text-blue-300/40 group-hover:text-blue-200',
                  collapsed ? 'w-10 h-10' : 'w-9 h-9'
                )}
              >
                {isActive && (
                  <div className="absolute inset-0 rounded-lg bg-blue-500/10" />
                )}
                <Icon className="w-[18px] h-[18px] relative z-10" strokeWidth={isActive ? 2.2 : 1.8} />
              </div>

              {/* Label */}
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -8 }}
                    transition={{ duration: 0.2, delay: 0.05 }}
                    className={cn(
                      'ml-3 text-[13px] font-medium whitespace-nowrap',
                      isActive ? 'text-white' : 'text-blue-200/60 group-hover:text-blue-100'
                    )}
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>

              {/* Active dot for collapsed */}
              {collapsed && isActive && (
                <motion.div
                  layoutId="active-dot"
                  className="absolute -right-0.5 top-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-[#5DADE2]"
                  style={{ boxShadow: '0 0 8px rgba(93,173,226,0.6)' }}
                />
              )}

              {/* Tooltip for collapsed */}
              {collapsed && (
                <div className="absolute left-full ml-3 px-3 py-1.5 bg-[#1B3A6B] text-white text-xs font-medium rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-[100] shadow-xl shadow-black/20 border border-white/5">
                  {item.label}
                  <div className="absolute left-0 top-1/2 -translate-x-1 -translate-y-1/2 w-2 h-2 bg-[#1B3A6B] rotate-45 border-l border-b border-white/5" />
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div className="relative z-10 p-3">
        {/* Divider */}
        <div className="h-px bg-gradient-to-r from-transparent via-white/8 to-transparent mb-3" />

        {/* User Card */}
        <div
          className={cn(
            'flex items-center gap-3 rounded-xl p-2.5 transition-all duration-300',
            collapsed ? 'justify-center' : '',
            'bg-white/[0.02] border border-white/[0.04]'
          )}
        >
          {/* Avatar */}
          <div className="relative shrink-0">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400/20 to-blue-600/10 flex items-center justify-center border border-blue-400/20">
              <User className="w-4 h-4 text-blue-300/70" strokeWidth={1.8} />
            </div>
            <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-[#122240]" />
          </div>

          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="flex-1 min-w-0 overflow-hidden"
              >
                <p className="text-[11px] font-semibold text-blue-200/80 truncate">
                  {user?.username}
                </p>
                <p className="text-[10px] text-blue-300/40 truncate">
                  Sesión activa
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Logout Button */}
        <button
          onClick={logout}
          className={cn(
            'mt-2 w-full flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-[13px] font-medium',
            'text-red-300/50 hover:text-red-200 hover:bg-red-500/10 transition-all duration-300',
            collapsed ? 'justify-center' : ''
          )}
        >
          <LogOut className="w-[18px] h-[18px] shrink-0" strokeWidth={1.8} />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="whitespace-nowrap overflow-hidden"
              >
                Cerrar sesión
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* ── Desktop Sidebar ── */}
      <motion.aside
        initial={false}
        animate={{ width: collapsed ? 76 : 268 }}
        transition={{ duration: 0.35, ease: [0.25, 0.46, 0.45, 0.94] }}
        className="fixed left-0 top-0 bottom-0 z-50 hidden lg:flex flex-col border-r border-white/5"
        style={{
          background: 'linear-gradient(165deg, #0a1628 0%, #122240 40%, #1a3260 100%)',
          boxShadow: collapsed
            ? '4px 0 20px rgba(0,0,0,0.15)'
            : '8px 0 32px rgba(0,0,0,0.25)',
        }}
      >
        {sidebarContent}
      </motion.aside>

      {/* ── Mobile Sidebar (Drawer) ── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            {/* Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 bg-black/60 z-[60] lg:hidden"
              onClick={() => setMobileOpen(false)}
              style={{ touchAction: 'none' }}
            />
            {/* Drawer */}
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
              className="fixed left-0 top-0 bottom-0 z-[70] w-[280px] flex flex-col border-r border-white/5 lg:hidden"
              style={{
                background: 'linear-gradient(165deg, #0a1628 0%, #122240 40%, #1a3260 100%)',
                boxShadow: '8px 0 32px rgba(0,0,0,0.35)',
              }}
            >
              {/* Close button */}
              <button
                onClick={() => setMobileOpen(false)}
                className="absolute top-4 right-4 z-20 p-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors lg:hidden"
              >
                <X className="w-5 h-5" />
              </button>
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* ── Desktop Toggle Button ── */}
      <motion.button
        onClick={toggle}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        className="fixed z-[60] w-7 h-7 rounded-full bg-gradient-to-br from-[#1B3A6B] to-[#254E9A] text-white border border-blue-400/30 flex items-center justify-center shadow-lg shadow-blue-900/30 hover:shadow-blue-500/20 transition-shadow hidden lg:flex"
        style={{
          top: 24,
          left: collapsed ? 66 : 254,
          transition: 'left 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        }}
      >
        {collapsed ? (
          <ChevronRight className="w-3.5 h-3.5" strokeWidth={2.5} />
        ) : (
          <ChevronLeft className="w-3.5 h-3.5" strokeWidth={2.5} />
        )}
      </motion.button>
    </>
  );
}
