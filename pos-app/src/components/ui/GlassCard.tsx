import clsx from "classnames";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
}

export default function GlassCard({ children, className }: GlassCardProps) {
  return <div className={clsx("glass-panel p-5", className)}>{children}</div>;
}
