import { useEffect } from "react";
import { Route, Routes, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { useAuth } from "./contexts/AuthContext";
import { useTranslation } from "react-i18next";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import POSPage from "./pages/POSPage";
import ProductsPage from "./pages/ProductsPage";
import CustomersPage from "./pages/CustomersPage";
import SuppliersPage from "./pages/SuppliersPage";
import ExpensesPage from "./pages/ExpensesPage";
import ReportsPage from "./pages/ReportsPage";
import SettingsPage from "./pages/SettingsPage";
import UsersPage from "./pages/UsersPage";
import Layout from "./components/Layout";

const pageTransition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 }
};

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AdminRoute({ children }: { children: JSX.Element }) {
  const { user } = useAuth();
  if (user?.role !== "admin") {
    return <Navigate to="/" replace />;
  }
  return children;
}

function App() {
  const location = useLocation();
  const { i18n } = useTranslation();
  const { settings } = useAuth();

  useEffect(() => {
    if (settings?.language) {
      i18n.changeLanguage(settings.language);
      document.dir = settings.language === "ar" ? "rtl" : "ltr";
    }
  }, [settings?.language, i18n]);

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/login"
          element={
            <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
              <LoginPage />
            </motion.div>
          }
        />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route
            index
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <DashboardPage />
              </motion.div>
            }
          />
          <Route
            path="pos"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <POSPage />
              </motion.div>
            }
          />
          <Route
            path="products"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <ProductsPage />
              </motion.div>
            }
          />
          <Route
            path="customers"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <CustomersPage />
              </motion.div>
            }
          />
          <Route
            path="suppliers"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <SuppliersPage />
              </motion.div>
            }
          />
          <Route
            path="expenses"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <ExpensesPage />
              </motion.div>
            }
          />
          <Route
            path="reports"
            element={
              <AdminRoute>
                <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                  <ReportsPage />
                </motion.div>
              </AdminRoute>
            }
          />
          <Route
            path="settings"
            element={
              <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                <SettingsPage />
              </motion.div>
            }
          />
          <Route
            path="users"
            element={
              <AdminRoute>
                <motion.div {...pageTransition} transition={{ duration: 0.4 }}>
                  <UsersPage />
                </motion.div>
              </AdminRoute>
            }
          />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default App;
