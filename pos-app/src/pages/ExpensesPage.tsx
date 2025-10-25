import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassButton from "../components/ui/GlassButton";
import GlassCard from "../components/ui/GlassCard";
import DataTable from "../components/DataTable";
import { Expense } from "../db/types";
import { useToast } from "../hooks/useToast";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [editing, setEditing] = useState<Partial<Expense> | null>(null);
  const toast = useToast();

  const loadExpenses = async () => {
    const list = await window.posAPI.listExpenses();
    setExpenses(list);
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  const saveExpense = async () => {
    if (!editing) return;
    await window.posAPI.saveExpense(editing);
    toast.success("تم حفظ المصروف");
    setEditing(null);
    loadExpenses();
  };

  const deleteExpense = async (id: number) => {
    await window.posAPI.deleteExpense(id);
    toast.info("تم حذف المصروف");
    loadExpenses();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="المصروفات"
        description="راقب مصروفات المحل اليومية"
        actions={<GlassButton onClick={() => setEditing({ title: "", amount: 0 })}>إضافة مصروف</GlassButton>}
      />
      <DataTable
        columns={[
          { key: "title", header: "العنوان" },
          { key: "amount", header: "المبلغ", render: (row) => row.amount.toFixed(2) },
          { key: "createdAt", header: "التاريخ" },
          {
            key: "actions",
            header: "إجراءات",
            render: (row) => (
              <div className="flex space-x-2 rtl:space-x-reverse">
                <GlassButton className="px-3 py-2" onClick={() => setEditing(row)}>تعديل</GlassButton>
                <GlassButton className="px-3 py-2" onClick={() => deleteExpense(row.id)}>حذف</GlassButton>
              </div>
            )
          }
        ]}
        data={expenses}
        emptyText="لا توجد مصروفات"
      />

      {editing && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <GlassCard className="w-full max-w-xl space-y-4">
            <h3 className="text-xl font-bold">{editing.id ? "تعديل مصروف" : "مصروف جديد"}</h3>
            <input className="neu-input" placeholder="العنوان" value={editing.title || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), title: event.target.value }))} />
            <input className="neu-input" type="number" placeholder="المبلغ" value={editing.amount ?? 0} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), amount: Number(event.target.value) }))} />
            <textarea className="neu-input" placeholder="ملاحظات" value={editing.notes || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), notes: event.target.value }))} />
            <div className="flex justify-end space-x-3 rtl:space-x-reverse">
              <GlassButton onClick={() => setEditing(null)}>إلغاء</GlassButton>
              <GlassButton onClick={saveExpense}>حفظ</GlassButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
