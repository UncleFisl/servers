import GlassCard from "./ui/GlassCard";
import GlassButton from "./ui/GlassButton";
import { SaleItemPayload } from "../db/types";
import { MinusIcon, PlusIcon, TrashIcon } from "@heroicons/react/24/outline";

interface POSCartProps {
  items: SaleItemPayload[];
  onQuantityChange: (id: number, quantity: number) => void;
  onRemove: (id: number) => void;
  onClear: () => void;
}

export default function POSCart({ items, onQuantityChange, onRemove, onClear }: POSCartProps) {
  const subtotal = items.reduce((acc, item) => acc + item.price * item.quantity, 0);

  return (
    <GlassCard className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-primary-dark">السلة</h3>
        <GlassButton className="px-4 py-2" onClick={onClear}>
          تفريغ
        </GlassButton>
      </div>
      <div className="space-y-3 max-h-72 overflow-y-auto pr-2">
        {items.length === 0 && <p className="text-sm text-gray-600">ابدأ بإضافة المنتجات إلى السلة.</p>}
        {items.map((item) => (
          <div key={item.id} className="glass-panel px-4 py-3 flex items-center justify-between">
            <div>
              <h4 className="font-semibold">{item.name}</h4>
              <p className="text-xs opacity-70">{item.price.toFixed(2)} × {item.quantity}</p>
            </div>
            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              <GlassButton
                className="px-3 py-2"
                onClick={() => onQuantityChange(item.id, Math.max(1, item.quantity - 1))}
              >
                <MinusIcon className="w-4 h-4" />
              </GlassButton>
              <span className="w-8 text-center font-semibold">{item.quantity}</span>
              <GlassButton className="px-3 py-2" onClick={() => onQuantityChange(item.id, item.quantity + 1)}>
                <PlusIcon className="w-4 h-4" />
              </GlassButton>
              <GlassButton className="px-3 py-2" onClick={() => onRemove(item.id)}>
                <TrashIcon className="w-4 h-4" />
              </GlassButton>
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center justify-between font-semibold text-lg">
        <span>الإجمالي الفرعي</span>
        <span>{subtotal.toFixed(2)}</span>
      </div>
    </GlassCard>
  );
}
