import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useTranslation } from "react-i18next";
import StatCard from "../components/ui/StatCard";
import PageHeader from "../components/PageHeader";
import { DashboardMetrics } from "../db/client";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import GlassCard from "../components/ui/GlassCard";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const { t } = useTranslation();
  const { settings } = useAuth();
  const currency = settings?.currency || "SAR";

  useEffect(() => {
    const load = async () => {
      const response = await window.posAPI.getDashboardMetrics();
      setMetrics(response);
    };
    load();
  }, []);

  return (
    <div>
      <PageHeader title={t("dashboard")} description="نظرة شاملة على أداء الصالون" />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard title={t("todaySales")} value={`${metrics?.today.total?.toFixed(2) || "0.00"} ${currency}`} />
        <StatCard title={t("monthSales")} value={`${metrics?.month.total?.toFixed(2) || "0.00"} ${currency}`} />
        <StatCard title={t("expensesTotal")} value={`${metrics?.expenses.total?.toFixed(2) || "0.00"} ${currency}`} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard>
          <h3 className="text-lg font-semibold text-primary-dark mb-4">اتجاه المبيعات خلال 14 يوم</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics?.salesTrend || []}>
                <XAxis dataKey="day" stroke="#6fb1fc" />
                <YAxis stroke="#6fb1fc" />
                <Tooltip formatter={(value) => [`${value} ${currency}`, "المبيعات"]} />
                <Line type="monotone" dataKey="total" stroke="#6fb1fc" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
        <GlassCard>
          <h3 className="text-lg font-semibold text-primary-dark mb-4">أفضل المنتجات مبيعًا</h3>
          <ul className="space-y-3">
            {metrics?.topProducts.map((product) => (
              <li key={product.name} className="flex items-center justify-between">
                <span className="font-medium">{product.name}</span>
                <span className="text-primary-dark">{product.qty}</span>
              </li>
            )) || <p className="text-sm text-gray-600">لا توجد بيانات حتى الآن.</p>}
          </ul>
        </GlassCard>
      </div>
    </div>
  );
}
