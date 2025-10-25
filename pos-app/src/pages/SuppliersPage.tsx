import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/ui/GlassCard";
import GlassButton from "../components/ui/GlassButton";
import DataTable from "../components/DataTable";
import { Contact } from "../db/types";
import { useToast } from "../hooks/useToast";

export default function SuppliersPage() {
  const toast = useToast();
  const [suppliers, setSuppliers] = useState<Contact[]>([]);
  const [editing, setEditing] = useState<Partial<Contact> | null>(null);

  const loadSuppliers = async () => {
    const data = await window.posAPI.listContacts("supplier");
    setSuppliers(data);
  };

  useEffect(() => {
    loadSuppliers();
  }, []);

  const save = async (contact: Partial<Contact>) => {
    if (!contact.name) {
      toast.error("أدخل الاسم");
      return;
    }
    await window.posAPI.saveContact({ type: "supplier", data: contact });
    toast.success("تم الحفظ بنجاح");
    loadSuppliers();
  };

  const remove = async (id: number) => {
    await window.posAPI.deleteContact({ type: "supplier", id });
    toast.info("تم حذف المورد");
    loadSuppliers();
  };

  const exportData = async () => {
    const result = await window.posAPI.exportContacts("supplier");
    if (result.success) {
      toast.success("تم إنشاء الملف", result.filePath);
    } else {
      toast.error("تعذر التصدير");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="الموردون"
        description="تعقب بيانات الموردين والفواتير"
        actions={
          <div className="flex space-x-3 rtl:space-x-reverse">
            <GlassButton onClick={() => setEditing({})}>إضافة مورد</GlassButton>
            <GlassButton onClick={exportData}>تصدير Excel</GlassButton>
          </div>
        }
      />
      <DataTable
        columns={[
          { key: "name", header: "الاسم" },
          { key: "phone", header: "الجوال" },
          { key: "email", header: "البريد" },
          {
            key: "actions",
            header: "إجراءات",
            render: (row) => (
              <div className="flex space-x-2 rtl:space-x-reverse">
                <GlassButton className="px-3 py-2" onClick={() => setEditing(row)}>تعديل</GlassButton>
                <GlassButton className="px-3 py-2" onClick={() => remove(row.id)}>حذف</GlassButton>
              </div>
            )
          }
        ]}
        data={suppliers}
        emptyText="لا يوجد موردون"
      />

      {editing && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <GlassCard className="w-full max-w-2xl space-y-4">
            <h3 className="text-xl font-bold">{editing.id ? "تعديل مورد" : "مورد جديد"}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input className="neu-input" placeholder="الاسم" value={editing.name || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), name: event.target.value }))} />
              <input className="neu-input" placeholder="الجوال" value={editing.phone || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), phone: event.target.value }))} />
              <input className="neu-input" placeholder="البريد" value={editing.email || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), email: event.target.value }))} />
              <input className="neu-input md:col-span-2" placeholder="ملاحظات" value={editing.notes || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), notes: event.target.value }))} />
            </div>
            <div className="flex justify-end space-x-3 rtl:space-x-reverse">
              <GlassButton onClick={() => setEditing(null)}>إلغاء</GlassButton>
              <GlassButton
                onClick={async () => {
                  if (!editing) return;
                  await save(editing);
                  setEditing(null);
                }}
              >
                حفظ
              </GlassButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
