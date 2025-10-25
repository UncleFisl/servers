import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassButton from "../components/ui/GlassButton";
import GlassCard from "../components/ui/GlassCard";
import DataTable from "../components/DataTable";
import { useToast } from "../hooks/useToast";
import { User } from "../contexts/AuthContext";

export default function UsersPage() {
  const toast = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [editing, setEditing] = useState<Partial<User & { password?: string }>>({});
  const [showForm, setShowForm] = useState(false);

  const loadUsers = async () => {
    const list = await window.posAPI.listUsers();
    setUsers(list as User[]);
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const saveUser = async () => {
    if (!editing?.username) {
      toast.error("أدخل اسم المستخدم");
      return;
    }
    await window.posAPI.saveUser(editing);
    toast.success("تم حفظ المستخدم");
    setShowForm(false);
    setEditing({});
    loadUsers();
  };

  const deleteUser = async (id: number) => {
    await window.posAPI.deleteUser(id);
    toast.info("تم حذف المستخدم");
    loadUsers();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="المستخدمون"
        description="إدارة صلاحيات الوصول"
        actions={<GlassButton onClick={() => { setEditing({}); setShowForm(true); }}>إضافة مستخدم</GlassButton>}
      />
      <DataTable
        columns={[
          { key: "username", header: "اسم المستخدم" },
          { key: "role", header: "الدور" },
          {
            key: "actions",
            header: "إجراءات",
            render: (row) => (
              <div className="flex space-x-2 rtl:space-x-reverse">
                <GlassButton className="px-3 py-2" onClick={() => { setEditing(row); setShowForm(true); }}>تعديل</GlassButton>
                <GlassButton className="px-3 py-2" onClick={() => deleteUser(row.id)}>حذف</GlassButton>
              </div>
            )
          }
        ]}
        data={users}
        emptyText="لا يوجد مستخدمون"
      />

      {showForm && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <GlassCard className="w-full max-w-xl space-y-4">
            <h3 className="text-xl font-bold">{editing?.id ? "تعديل مستخدم" : "مستخدم جديد"}</h3>
            <input className="neu-input" placeholder="اسم المستخدم" value={editing?.username || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), username: event.target.value }))} />
            <input className="neu-input" placeholder="كلمة المرور" type="password" value={editing?.password || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), password: event.target.value }))} />
            <select className="neu-input" value={editing?.role || "cashier"} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), role: event.target.value as User["role"] }))}>
              <option value="admin">مدير</option>
              <option value="cashier">كاشير</option>
            </select>
            <div className="flex justify-end space-x-3 rtl:space-x-reverse">
              <GlassButton onClick={() => setShowForm(false)}>إلغاء</GlassButton>
              <GlassButton onClick={saveUser}>حفظ</GlassButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
