import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "../hooks/useToast";
import { useSettings, Settings } from "./SettingsContext";

export interface User {
  id: number;
  username: string;
  role: "admin" | "cashier";
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  settings: Settings | null;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();
  const { settings, refreshSettings } = useSettings();

  useEffect(() => {
    refreshSettings();
  }, [refreshSettings]);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const response = await window.posAPI.login({ username, password });
      if (!response.success) {
        toast.error(response.message || "فشل تسجيل الدخول");
        return false;
      }
      setUser(response.user);
      toast.success("تم تسجيل الدخول بنجاح");
      navigate("/");
      return true;
    } catch (error) {
      console.error("Login error", error);
      toast.error("تعذر الاتصال بالقاعدة");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, settings }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
