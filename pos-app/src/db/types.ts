export interface Product {
  id: number;
  name: string;
  barcode?: string;
  price: number;
  cost: number;
  quantity: number;
  lowStockThreshold: number;
  category?: string;
  image?: string | null;
}

export interface Contact {
  id: number;
  name: string;
  phone?: string;
  email?: string;
  notes?: string;
}

export interface Expense {
  id: number;
  title: string;
  amount: number;
  createdAt: string;
  notes?: string;
}

export interface SaleItemPayload {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

export interface SalePayload {
  items: SaleItemPayload[];
  discount: number;
  taxRate: number;
  paymentMethod: "cash" | "card" | "mixed";
  paidAmount: number;
  customerId?: number | null;
  userId: number;
}
