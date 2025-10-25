import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/ui/GlassCard";
import GlassButton from "../components/ui/GlassButton";
import POSCart from "../components/POSCart";
import { Product, SaleItemPayload } from "../db/types";
import { useAuth } from "../contexts/AuthContext";
import { useSettings } from "../contexts/SettingsContext";
import printJS from "print-js";
import jsPDF from "jspdf";
import { useToast } from "../hooks/useToast";
import { useTranslation } from "react-i18next";

export default function POSPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState("");
  const [cart, setCart] = useState<SaleItemPayload[]>([]);
  const [discount, setDiscount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState<"cash" | "card" | "mixed">("cash");
  const [paidAmount, setPaidAmount] = useState(0);
  const { user } = useAuth();
  const { settings } = useSettings();
  const toast = useToast();
  const { t } = useTranslation();
  const currency = settings?.currency || "SAR";

  useEffect(() => {
    const loadProducts = async () => {
      const list = await window.posAPI.searchProducts("");
      setProducts(list);
    };
    loadProducts();
  }, []);

  const filteredProducts = useMemo(() => {
    if (!query) return products;
    return products.filter((product) =>
      product.name.toLowerCase().includes(query.toLowerCase()) || product.barcode?.includes(query)
    );
  }, [products, query]);

  const addToCart = (product: Product) => {
    setCart((prev) => {
      const exists = prev.find((item) => item.id === product.id);
      if (exists) {
        return prev.map((item) => (item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
      }
      return [...prev, { id: product.id, name: product.name, price: product.price, quantity: 1 }];
    });
  };

  const removeFromCart = (id: number) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  const updateQuantity = (id: number, quantity: number) => {
    setCart((prev) => prev.map((item) => (item.id === id ? { ...item, quantity } : item)));
  };

  const clearCart = () => setCart([]);

  const subtotal = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  const tax = (subtotal - discount) * (settings?.taxRate || 0);
  const total = subtotal - discount + tax;
  const changeAmount = paidAmount - total;

  const handleCheckout = async () => {
    if (!cart.length || !user) {
      toast.error("أضف منتجات أولاً");
      return;
    }
    try {
      const payload = {
        items: cart,
        discount,
        taxRate: settings?.taxRate || 0,
        paymentMethod,
        paidAmount,
        userId: user.id
      };
      const result = await window.posAPI.createSale(payload);
      toast.success("تم حفظ الفاتورة", `رقم العملية ${result.saleId}`);
      generateInvoice(result.saleId);
      const list = await window.posAPI.searchProducts("");
      setProducts(list);
      clearCart();
      setDiscount(0);
      setPaidAmount(0);
    } catch (error) {
      console.error(error);
      toast.error("تعذر حفظ الفاتورة");
    }
  };

  const generateInvoice = (saleId: number) => {
    const invoiceElement = document.getElementById("invoice-area");
    if (!invoiceElement) return;

    const receiptType = settings?.receiptType || "thermal";

    if (receiptType === "thermal") {
      printJS({
        printable: "invoice-area",
        type: "html",
        css: "",
        style: "body{direction: rtl; font-family: 'Cairo', sans-serif;}"
      });
    } else {
      const doc = new jsPDF();
      doc.text(`${settings?.storeName || "Barber POS"}`, 10, 10);
      doc.text(`Invoice #${saleId}`, 10, 20);
      doc.text(`Total: ${total.toFixed(2)} ${settings?.currency}`, 10, 30);
      doc.save(`invoice-${saleId}.pdf`);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("pos")}
        description="إدارة عملية البيع بكفاءة تامة"
        actions={<GlassButton onClick={handleCheckout}>إتمام</GlassButton>}
      />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <GlassCard>
            <input
              className="neu-input w-full"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && filteredProducts.length > 0) {
                  addToCart(filteredProducts[0]);
                  setQuery("");
                }
              }}
              placeholder={t("searchProducts")}
            />
          </GlassCard>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4 max-h-[520px] overflow-y-auto pr-3">
            {filteredProducts.map((product) => (
              <button
                key={product.id}
                className="glass-panel p-4 text-left rounded-3xl hover:-translate-y-1 transition-transform"
                onClick={() => addToCart(product)}
              >
                <div className="flex justify-between items-start">
                  <h4 className="font-semibold text-primary-dark">{product.name}</h4>
                  <span className="text-sm bg-primary/20 text-primary-dark px-3 py-1 rounded-full">
                    {product.price.toFixed(2)} {currency}
                  </span>
                </div>
                <p className="text-xs mt-2 opacity-70">Barcode: {product.barcode || "--"}</p>
                <p className="text-xs opacity-60">المتوفر: {product.quantity}</p>
              </button>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          <POSCart items={cart} onQuantityChange={updateQuantity} onRemove={removeFromCart} onClear={clearCart} />
          <GlassCard className="space-y-4">
            <div className="flex items-center justify-between">
              <span>الخصم</span>
              <input
                type="number"
                className="neu-input w-32 text-center"
                value={discount}
                onChange={(event) => setDiscount(Number(event.target.value))}
              />
            </div>
            <div className="flex items-center justify-between">
              <span>طريقة الدفع</span>
              <select className="neu-input w-40" value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value as any)}>
                <option value="cash">{t("cash")}</option>
                <option value="card">{t("card")}</option>
                <option value="mixed">{t("mixed")}</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <span>المبلغ المدفوع</span>
              <input
                type="number"
                className="neu-input w-32 text-center"
                value={paidAmount}
                onChange={(event) => setPaidAmount(Number(event.target.value))}
              />
            </div>
            <div className="border-t border-white/50 pt-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span>الإجمالي الفرعي</span>
                <span>{subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>الضريبة ({(settings?.taxRate || 0) * 100}%)</span>
                <span>{tax.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-lg font-semibold">
                <span>{t("total")}</span>
                <span>
                  {total.toFixed(2)} {currency}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span>الباقي</span>
                <span className={changeAmount < 0 ? "text-red-500" : "text-green-600"}>{changeAmount.toFixed(2)}</span>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      <div id="invoice-area" className="hidden">
        <h2>{settings?.storeName}</h2>
        <p>ملخص الفاتورة</p>
        <ul>
          {cart.map((item) => (
            <li key={item.id}>
              {item.name} - {item.quantity} × {item.price}
            </li>
          ))}
        </ul>
        <p>
          الإجمالي: {total.toFixed(2)} {currency}
        </p>
      </div>
    </div>
  );
}
