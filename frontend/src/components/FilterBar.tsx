import { motion } from 'framer-motion';
import { Filter } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FilterBarProps {
  children: React.ReactNode;
  className?: string;
}

export function FilterBar({ children, className }: FilterBarProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 }}
      className={cn(
        'relative overflow-hidden rounded-2xl bg-white border border-slate-100 shadow-sm',
        className
      )}
    >
      {/* Top accent line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-congroup-blue via-congroup-blue-med to-congroup-blue/30" />

      <div className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-congroup-blue/8">
            <Filter className="w-3.5 h-3.5 text-congroup-blue" />
          </div>
          <h2 className="text-xs font-bold text-congroup-blue uppercase tracking-widest">
            Filtros
          </h2>
        </div>
        <div className="flex flex-wrap items-end gap-4">
          {children}
        </div>
      </div>
    </motion.div>
  );
}
