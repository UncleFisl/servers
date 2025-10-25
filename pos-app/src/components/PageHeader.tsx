import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export default function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
      <div>
        <h2 className="text-2xl font-bold text-primary-dark">{title}</h2>
        {description && <p className="text-sm text-gray-600 mt-1">{description}</p>}
      </div>
      {actions && <div className="flex items-center space-x-3 rtl:space-x-reverse">{actions}</div>}
    </div>
  );
}
