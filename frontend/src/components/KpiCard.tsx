import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  label: string;
  value: string | number;
  color: string;
  icon: LucideIcon;
  subtitle?: string;
  index?: number;
}

export function KpiCard({ label, value, color, icon: Icon, subtitle, index = 0 }: KpiCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 + index * 0.05, duration: 0.4 }}
      className="group relative overflow-hidden rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-300"
    >
      {/* Subtle gradient accent */}
      <div
        className="absolute top-0 left-0 right-0 h-1 opacity-60"
        style={{ background: `linear-gradient(90deg, ${color}, ${color}66)` }}
      />

      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
              {label}
            </p>
            <p
              className="text-2xl font-bold tracking-tight"
              style={{ color }}
            >
              {value}
            </p>
            {subtitle && (
              <p className="text-[11px] text-slate-400 mt-1 font-medium">
                {subtitle}
              </p>
            )}
          </div>

          <div
            className="flex items-center justify-center w-8 h-8 md:w-10 md:h-10 rounded-lg md:rounded-xl shrink-0 ml-2 md:ml-3"
            style={{ background: `${color}11` }}
          >
            <Icon className="w-4 h-4 md:w-5 md:h-5" style={{ color }} strokeWidth={1.8} />
          </div>
        </div>
      </div>

      {/* Hover glow */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: `radial-gradient(circle at 80% 20%, ${color}08 0%, transparent 60%)`,
        }}
      />
    </motion.div>
  );
}
