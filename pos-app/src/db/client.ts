import { Contact, Expense, Product, SalePayload } from "./types";

export interface DashboardMetrics {
  today: { total: number; orders: number };
  month: { total: number; orders: number };
  expenses: { total: number };
  topProducts: { name: string; qty: number }[];
  salesTrend: { day: string; total: number }[];
}

export interface SettingsDTO {
  id?: number;
  language: "ar" | "en";
  currency: string;
  taxRate: number;
  storeName: string;
  logoPath?: string | null;
  receiptType: "thermal" | "a4";
}

export interface UserDTO {
  id: number;
  username: string;
  role: "admin" | "cashier";
}

export interface PosAPI {
  login: (payload: { username: string; password: string }) => Promise<{ success: boolean; message?: string; user?: UserDTO }>;
  getDashboardMetrics: () => Promise<DashboardMetrics>;
  searchProducts: (query?: string) => Promise<Product[]>;
  createSale: (payload: SalePayload) => Promise<{ saleId: number; total: number; taxValue: number; discountValue: number; changeAmount: number }>;
  listProducts: () => Promise<Product[]>;
  saveProduct: (payload: Partial<Product>) => Promise<{ id: number }>;
  deleteProduct: (id: number) => Promise<{ success: boolean }>;
  importProducts: () => Promise<{ success: boolean; imported?: number }>;
  exportProducts: () => Promise<{ success: boolean; filePath?: string }>;
  listContacts: (type: "customer" | "supplier") => Promise<Contact[]>;
  saveContact: (payload: { type: "customer" | "supplier"; data: Partial<Contact> }) => Promise<{ id: number }>;
  deleteContact: (payload: { type: "customer" | "supplier"; id: number }) => Promise<{ success: boolean }>;
  exportContacts: (type: "customer" | "supplier") => Promise<{ success: boolean; filePath?: string }>;
  listExpenses: () => Promise<Expense[]>;
  saveExpense: (payload: Partial<Expense>) => Promise<{ id: number }>;
  deleteExpense: (id: number) => Promise<{ success: boolean }>;
  salesReport: (payload: { from: string; to: string; userId?: number }) => Promise<any[]>;
  exportReport: (payload: { type: "excel" | "json"; rows: any[] }) => Promise<{ success: boolean; filePath?: string; message?: string }>;
  getSettings: () => Promise<SettingsDTO>;
  saveSettings: (payload: SettingsDTO) => Promise<{ success: boolean }>;
  uploadLogo: () => Promise<{ success: boolean; logoPath?: string }>;
  listUsers: () => Promise<UserDTO[]>;
  saveUser: (payload: Partial<UserDTO> & { password?: string }) => Promise<{ id: number }>;
  deleteUser: (id: number) => Promise<{ success: boolean }>;
}
