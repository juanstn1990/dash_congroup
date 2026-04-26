import { motion } from 'framer-motion';
import { FileSearch } from 'lucide-react';

interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-6 bg-white rounded-2xl border border-slate-100 shadow-sm"
    >
      <div className="w-14 h-14 rounded-2xl bg-slate-50 flex items-center justify-center mb-4">
        <FileSearch className="w-7 h-7 text-slate-300" strokeWidth={1.5} />
      </div>
      <p className="text-sm text-slate-400 font-medium text-center max-w-sm">
        {message}
      </p>
    </motion.div>
  );
}
