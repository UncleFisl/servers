import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassButton from "../components/ui/GlassButton";
import GlassCard from "../components/ui/GlassCard";
import DataTable from "../components/DataTable";
import { useToast } from "../hooks/useToast";
import jsPDF from "jspdf";
import { useSettings } from "../contexts/SettingsContext";

interface SaleReportRow {
  id: number;
  customerId: number | null;
  total: number;
  discount: number;
  tax: number;
  paymentMethod: string;
  paidAmount: number;
  changeAmount: number;
  userId: number;
  createdAt: string;
  username?: string;
}

export default function ReportsPage() {
  const toast = useToast();
  const [rows, setRows] = useState<SaleReportRow[]>([]);
  const [dateRange, setDateRange] = useState({ from: new Date().toISOString().slice(0, 10), to: new Date().toISOString().slice(0, 10) });
  const { settings } = useSettings();
  const currency = settings?.currency || "SAR";

  const loadReport = async () => {
    const report = await window.posAPI.salesReport(dateRange);
    setRows(report);
  };

  useEffect(() => {
    loadReport();
  }, []);

  const exportExcel = async () => {
    const result = await window.posAPI.exportReport({ type: "excel", rows });
    if (result.success) {
      toast.success("تم إنشاء تقرير Excel", result.filePath);
    } else {
      toast.error(result.message || "لا توجد بيانات للتصدير");
    }
  };

  const exportPDF = () => {
    if (!rows.length) {
      toast.error("لا توجد بيانات للتصدير");
      return;
    }
    const doc = new jsPDF();
    doc.text("تقرير المبيعات", 10, 10);
    rows.slice(0, 20).forEach((row, index) => {
      doc.text(`${row.createdAt} - ${row.total.toFixed(2)}`, 10, 20 + index * 8);
    });
    doc.save("sales-report.pdf");
    toast.success("تم تنزيل PDF");
  };

  const totals = rows.reduce(
    (acc, row) => {
      acc.total += row.total;
      acc.tax += row.tax;
      acc.count += 1;
      return acc;
    },
    { total: 0, tax: 0, count: 0 }
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="التقارير"
        description="تتبع المبيعات حسب المدة"
        actions={
          <div className="flex space-x-3 rtl:space-x-reverse">
            <GlassButton onClick={exportExcel}>تصدير Excel</GlassButton>
            <GlassButton onClick={exportPDF}>تصدير PDF</GlassButton>
          </div>
        }
      />
      <GlassCard className="flex flex-wrap gap-4 items-end">
        <div className="space-y-2">
          <label className="text-sm font-semibold">من</label>
          <input type="date" className="neu-input" value={dateRange.from} onChange={(event) => setDateRange((prev) => ({ ...prev, from: event.target.value }))} />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold">إلى</label>
          <input type="date" className="neu-input" value={dateRange.to} onChange={(event) => setDateRange((prev) => ({ ...prev, to: event.target.value }))} />
        </div>
        <GlassButton onClick={loadReport}>عرض التقرير</GlassButton>
        <div className="ml-auto rtl:mr-auto text-sm space-y-1">
          <p>
            الإجمالي: {totals.total.toFixed(2)} {currency}
          </p>
          <p>
            الضرائب: {totals.tax.toFixed(2)} {currency}
          </p>
          <p>عدد الفواتير: {totals.count}</p>
        </div>
      </GlassCard>

      <DataTable
        columns={[
          { key: "createdAt", header: "التاريخ" },
          { key: "total", header: "الإجمالي", render: (row) => `${row.total.toFixed(2)} ${currency}` },
          { key: "tax", header: "الضريبة", render: (row) => `${row.tax.toFixed(2)} ${currency}` },
          { key: "paymentMethod", header: "الدفع" },
          { key: "username", header: "المستخدم" }
        ]}
        data={rows}
        emptyText="لا توجد مبيعات في المدة"
      />
    </div>
  );
}
