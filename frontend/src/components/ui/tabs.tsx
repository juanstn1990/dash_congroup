import * as React from "react";
import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";

interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
  className?: string;
}

const TabsContext = React.createContext<{ value: string; onValueChange: (v: string) => void } | null>(null);

function Tabs({ value, onValueChange, children, className }: TabsProps) {
  return (
    <TabsContext.Provider value={{ value, onValueChange }}>
      <div className={cn("w-full", className)}>{children}</div>
    </TabsContext.Provider>
  );
}

function TabsList({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("inline-flex flex-wrap items-center gap-1 rounded-xl bg-slate-100/80 p-1.5 border border-slate-200/60", className)}>
      {children}
    </div>
  );
}

interface TabsTriggerProps {
  value: string;
  className?: string;
  children: React.ReactNode;
  icon?: LucideIcon;
  color?: string;
}

function TabsTrigger({ value, className, children, icon: Icon, color = "#1B3A6B" }: TabsTriggerProps) {
  const ctx = React.useContext(TabsContext);
  if (!ctx) throw new Error("TabsTrigger must be inside Tabs");
  const active = ctx.value === value;

  return (
    <button
      onClick={() => ctx.onValueChange(value)}
      className={cn(
        "relative inline-flex items-center gap-1.5 md:gap-2 rounded-lg px-2.5 md:px-4 py-2 md:py-2.5 text-xs md:text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        active
          ? "text-white shadow-md"
          : "text-slate-500 hover:text-slate-700 hover:bg-white/60",
        className
      )}
      style={active ? { background: `linear-gradient(135deg, ${color}, ${color}dd)` } : {}}
    >
      {Icon && (
        <Icon className="w-4 h-4" strokeWidth={active ? 2.2 : 1.8} />
      )}
      <span>{children}</span>
    </button>
  );
}

function TabsContent({ value, className, children }: { value: string; className?: string; children: React.ReactNode }) {
  const ctx = React.useContext(TabsContext);
  if (!ctx) throw new Error("TabsContent must be inside Tabs");
  if (ctx.value !== value) return null;
  return <div className={cn("mt-5", className)}>{children}</div>;
}

export { Tabs, TabsList, TabsTrigger, TabsContent };
