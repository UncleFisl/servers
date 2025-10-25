import { createContext, useCallback, useContext, useMemo, useState, ReactNode } from "react";
import { AnimatePresence, motion } from "framer-motion";

interface ToastMessage {
  id: number;
  type: "success" | "error" | "info";
  title: string;
  description?: string;
}

interface ToastContextValue {
  push: (toast: Omit<ToastMessage, "id">) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ToastMessage[]>([]);

  const push = useCallback((toast: Omit<ToastMessage, "id">) => {
    setMessages((prev) => [...prev, { id: Date.now(), ...toast }]);
    setTimeout(() => {
      setMessages((prev) => prev.slice(1));
    }, 4000);
  }, []);

  const value = useMemo(() => ({ push }), [push]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed top-6 right-6 z-50 space-y-3 rtl:right-auto rtl:left-6">
        <AnimatePresence>
          {messages.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 40 }}
              className={`glass-panel px-5 py-4 border-l-4 rtl:border-r-4 ${
                toast.type === "success"
                  ? "border-green-400"
                  : toast.type === "error"
                    ? "border-red-400"
                    : "border-blue-400"
              }`}
            >
              <h4 className="font-semibold">{toast.title}</h4>
              {toast.description && <p className="text-sm opacity-80">{toast.description}</p>}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToastContext() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToastContext must be used within ToastProvider");
  }
  return context;
}
