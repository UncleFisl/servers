import { ReactNode } from "react";
import GlassCard from "./GlassCard";

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: ReactNode;
  footer?: string;
}

export default function StatCard({ title, value, icon, footer }: StatCardProps) {
  return (
    <GlassCard className="flex flex-col space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm uppercase tracking-widest opacity-70">{title}</span>
        {icon && <div className="text-primary-dark">{icon}</div>}
      </div>
      <div className="text-3xl font-bold text-primary-dark">{value}</div>
      {footer && <span className="text-xs opacity-70">{footer}</span>}
    </GlassCard>
  );
}
