import i18n from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  ar: {
    translation: {
      login: "تسجيل الدخول",
      username: "اسم المستخدم",
      password: "كلمة المرور",
      dashboard: "لوحة التحكم",
      pos: "نقطة البيع",
      products: "المنتجات",
      customers: "العملاء",
      suppliers: "الموردون",
      expenses: "المصروفات",
      reports: "التقارير",
      settings: "الإعدادات",
      users: "المستخدمون",
      logout: "تسجيل الخروج",
      welcomeBack: "مرحبًا بعودتك",
      totalSales: "إجمالي المبيعات",
      todaySales: "مبيعات اليوم",
      monthSales: "مبيعات الشهر",
      expensesTotal: "إجمالي المصروفات",
      lowStock: "تنبيه المخزون",
      add: "إضافة",
      edit: "تعديل",
      delete: "حذف",
      save: "حفظ",
      cancel: "إلغاء",
      searchProducts: "ابحث عن منتج أو باركود",
      paymentMethod: "طريقة الدفع",
      discount: "الخصم",
      tax: "الضريبة",
      cash: "نقدي",
      card: "بطاقة",
      mixed: "متعدد",
      quantity: "الكمية",
      price: "السعر",
      total: "الإجمالي",
      actions: "إجراءات",
      export: "تصدير",
      import: "استيراد",
      print: "طباعة",
      downloadPDF: "تحميل PDF"
    }
  },
  en: {
    translation: {
      login: "Login",
      username: "Username",
      password: "Password",
      dashboard: "Dashboard",
      pos: "Point of Sale",
      products: "Products",
      customers: "Customers",
      suppliers: "Suppliers",
      expenses: "Expenses",
      reports: "Reports",
      settings: "Settings",
      users: "Users",
      logout: "Log out",
      welcomeBack: "Welcome back",
      totalSales: "Total Sales",
      todaySales: "Today Sales",
      monthSales: "Monthly Sales",
      expensesTotal: "Total Expenses",
      lowStock: "Low Stock Alert",
      add: "Add",
      edit: "Edit",
      delete: "Delete",
      save: "Save",
      cancel: "Cancel",
      searchProducts: "Search product or barcode",
      paymentMethod: "Payment Method",
      discount: "Discount",
      tax: "Tax",
      cash: "Cash",
      card: "Card",
      mixed: "Mixed",
      quantity: "Quantity",
      price: "Price",
      total: "Total",
      actions: "Actions",
      export: "Export",
      import: "Import",
      print: "Print",
      downloadPDF: "Download PDF"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "ar",
    fallbackLng: "ar",
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
