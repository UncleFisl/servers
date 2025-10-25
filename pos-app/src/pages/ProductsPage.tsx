import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassButton from "../components/ui/GlassButton";
import DataTable from "../components/DataTable";
import { Product } from "../db/types";
import { useToast } from "../hooks/useToast";
import { useAuth } from "../contexts/AuthContext";
import GlassCard from "../components/ui/GlassCard";

interface ProductFormState extends Partial<Product> {}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<ProductFormState | null>(null);
  const [showForm, setShowForm] = useState(false);
  const toast = useToast();
  const { user } = useAuth();

  const loadProducts = async () => {
    const list = await window.posAPI.listProducts();
    setProducts(list);
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const filtered = useMemo(() => {
    if (!search) return products;
    return products.filter((product) => product.name.toLowerCase().includes(search.toLowerCase()));
  }, [products, search]);

  const handleSave = async () => {
    if (!editing) return;
    if (!editing.name) {
      toast.error("أدخل اسم المنتج");
      return;
    }
    await window.posAPI.saveProduct(editing);
    toast.success("تم حفظ المنتج");
    setShowForm(false);
    setEditing(null);
    loadProducts();
  };

  const handleDelete = async (id: number) => {
    if (user?.role !== "admin") {
      toast.error("لا تملك صلاحية الحذف");
      return;
    }
    await window.posAPI.deleteProduct(id);
    toast.info("تم حذف المنتج");
    loadProducts();
  };

  const handleImport = async () => {
    const result = await window.posAPI.importProducts();
    if (result.success) {
      toast.success(`تم استيراد ${result.imported} منتج`);
      loadProducts();
    } else {
      toast.error("لم يتم استيراد أي بيانات");
    }
  };

  const handleExport = async () => {
    const result = await window.posAPI.exportProducts();
    if (result.success) {
      toast.success("تم حفظ الملف", result.filePath);
    } else {
      toast.error("تعذر إنشاء الملف");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="المنتجات"
        description="إدارة جميع الخدمات ومنتجات البيع بالتجزئة"
        actions={
          <div className="flex space-x-3 rtl:space-x-reverse">
            <GlassButton onClick={() => { setEditing({}); setShowForm(true); }}>إضافة منتج</GlassButton>
            <GlassButton onClick={handleImport}>استيراد CSV</GlassButton>
            <GlassButton onClick={handleExport}>تصدير CSV</GlassButton>
          </div>
        }
      />
      <GlassCard>
        <input className="neu-input w-full" placeholder="بحث" value={search} onChange={(event) => setSearch(event.target.value)} />
      </GlassCard>
      <DataTable
        columns={[
          { key: "name", header: "الاسم" },
          { key: "barcode", header: "الباركود" },
          { key: "price", header: "السعر", render: (row) => `${row.price.toFixed(2)}` },
          {
            key: "quantity",
            header: "الكمية",
            render: (row) => (
              <span className={row.quantity <= row.lowStockThreshold ? "text-red-500 font-semibold" : ""}>{row.quantity}</span>
            )
          },
          {
            key: "actions",
            header: "إجراءات",
            render: (row) => (
              <div className="flex space-x-2 rtl:space-x-reverse">
                <GlassButton className="px-3 py-2" onClick={() => { setEditing(row); setShowForm(true); }}>تعديل</GlassButton>
                {user?.role === "admin" && (
                  <GlassButton className="px-3 py-2" onClick={() => handleDelete(row.id)}>حذف</GlassButton>
                )}
              </div>
            )
          }
        ]}
        data={filtered}
        emptyText="لا توجد منتجات"
      />

      {showForm && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-6 z-50">
          <GlassCard className="w-full max-w-2xl space-y-4">
            <h3 className="text-xl font-bold">{editing?.id ? "تعديل منتج" : "إضافة منتج"}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input className="neu-input" placeholder="الاسم" value={editing?.name || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), name: event.target.value }))} />
              <input className="neu-input" placeholder="الباركود" value={editing?.barcode || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), barcode: event.target.value }))} />
              <input className="neu-input" type="number" placeholder="السعر" value={editing?.price ?? 0} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), price: Number(event.target.value) }))} />
              <input className="neu-input" type="number" placeholder="التكلفة" value={editing?.cost ?? 0} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), cost: Number(event.target.value) }))} />
              <input className="neu-input" type="number" placeholder="الكمية" value={editing?.quantity ?? 0} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), quantity: Number(event.target.value) }))} />
              <input className="neu-input" type="number" placeholder="حد انخفاض المخزون" value={editing?.lowStockThreshold ?? 0} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), lowStockThreshold: Number(event.target.value) }))} />
              <input className="neu-input" placeholder="الفئة" value={editing?.category || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), category: event.target.value }))} />
              <input className="neu-input" placeholder="رابط الصورة" value={editing?.image || ""} onChange={(event) => setEditing((prev) => ({ ...(prev || {}), image: event.target.value }))} />
            </div>
            <div className="flex justify-end space-x-3 rtl:space-x-reverse">
              <GlassButton onClick={() => { setShowForm(false); setEditing(null); }}>إلغاء</GlassButton>
              <GlassButton onClick={handleSave}>حفظ</GlassButton>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
