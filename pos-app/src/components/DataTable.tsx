import { ReactNode } from "react";
import GlassCard from "./ui/GlassCard";

interface DataTableProps<T> {
  columns: { key: keyof T | string; header: string; render?: (row: T) => ReactNode }[];
  data: T[];
  emptyText?: string;
}

export default function DataTable<T extends { id?: number | string }>({ columns, data, emptyText }: DataTableProps<T>) {
  return (
    <GlassCard className="overflow-x-auto p-0">
      <table className="min-w-full divide-y divide-white/50">
        <thead className="bg-white/30">
          <tr>
            {columns.map((column) => (
              <th key={column.key as string} className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-gray-600 text-left rtl:text-right">
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-white/40">
          {data.length === 0 && (
            <tr>
              <td className="px-5 py-6 text-center text-sm text-gray-500" colSpan={columns.length}>
                {emptyText || "لا توجد بيانات"}
              </td>
            </tr>
          )}
          {data.map((row) => (
            <tr key={String(row.id)} className="hover:bg-white/40 transition-colors">
              {columns.map((column) => (
                <td key={column.key as string} className="px-5 py-4 text-sm text-gray-700 whitespace-nowrap">
                  {column.render ? column.render(row) : ((row as any)[column.key] ?? "-")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </GlassCard>
  );
}
