import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/ui/GlassCard";
import GlassButton from "../components/ui/GlassButton";
import DataTable from "../components/DataTable";
import { Contact } from "../db/types";
import { useToast } from "../hooks/useToast";

function useContacts(type: "customer" | "supplier") {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const toast = useToast();

  const loadContacts = async () => {
    const data = await window.posAPI.listContacts(type);
    setContacts(data);
  };

  useEffect(() => {
    loadContacts();
  }, []);

  const save = async (contact: Partial<Contact>) => {
    if (!contact.name) {
      toast.error("أدخل الاسم");
      return;
    }
    await window.posAPI.saveContact({ type, data: contact });
    toast.success("تم الحفظ بنجاح");
    loadContacts();
  };

  const remove = async (id: number) => {
    await window.posAPI.deleteContact({ type, id });
    toast.info("تم حذف السجل");
    loadContacts();
  };

  const exportData = async () => {
    const result = await window.posAPI.exportContacts(type);
    if (result.success) {
      toast.success("تم إنشاء الملف", result.filePath);
    } else {
      toast.error("تعذر التصدير");
    }
  };

  return { contacts, save, remove, exportData, refresh: loadContacts };
}

function ContactForm({ contact, onChange }: { contact: Partial<Contact>; onChange: (values: Partial<Contact>) => void }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <input className="neu-input" placeholder="الاسم" value={contact.name || ""} onChange={(event) => onChange({ ...contact, name: event.target.value })} />
      <input className="neu-input" placeholder="الجوال" value={contact.phone || ""} onChange={(event) => onChange({ ...contact, phone: event.target.value })} />
      <input className="neu-input" placeholder="البريد" value={contact.email || ""} onChange={(event) => onChange({ ...contact, email: event.target.value })} />
      <input className="neu-input md:col-span-2" placeholder="ملاحظات" value={contact.notes || ""} onChange={(event) => onChange({ ...contact, notes: event.target.value })} />
    </div>
  );
}

export default function CustomersPage() {
  const { contacts, save, remove, exportData } = useContacts("customer");
  const [editing, setEditing] = useState<Partial<Contact> | null>(null);

  return (
    <div className="space-y-6">
      <PageHeader
        title="العملاء"
        description="إدارة بيانات العملاء وتواصلهم"
        actions={
          <div className="flex space-x-3 rtl:space-x-reverse">
            <GlassButton onClick={() => setEditing({})}>إضافة عميل</GlassButton>
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
        data={contacts}
        emptyText="لا يوجد عملاء"
      />
      {editing && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <GlassCard className="w-full max-w-2xl space-y-4">
            <h3 className="text-xl font-bold">{editing.id ? "تعديل عميل" : "عميل جديد"}</h3>
            <ContactForm
              contact={editing}
              onChange={(values) => setEditing(values)}
            />
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
