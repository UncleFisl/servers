import { Outlet, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../contexts/AuthContext";
import { useSettings } from "../contexts/SettingsContext";
import GlassCard from "./ui/GlassCard";
import GlassButton from "./ui/GlassButton";
import { Bars3Icon, Cog6ToothIcon, CurrencyDollarIcon, HomeIcon, ShoppingBagIcon, UserGroupIcon, UsersIcon, ClipboardDocumentListIcon, QueueListIcon } from "@heroicons/react/24/outline";

const navLinks = [
  { to: "/", labelKey: "dashboard", icon: HomeIcon },
  { to: "/pos", labelKey: "pos", icon: CurrencyDollarIcon },
  { to: "/products", labelKey: "products", icon: ShoppingBagIcon },
  { to: "/customers", labelKey: "customers", icon: UserGroupIcon },
  { to: "/suppliers", labelKey: "suppliers", icon: UsersIcon },
  { to: "/expenses", labelKey: "expenses", icon: QueueListIcon },
  { to: "/reports", labelKey: "reports", icon: ClipboardDocumentListIcon, role: "admin" as const },
  { to: "/settings", labelKey: "settings", icon: Cog6ToothIcon }
];

export default function Layout() {
  const { t } = useTranslation();
  const { logout, user } = useAuth();
  const { settings } = useSettings();

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-accent/30 to-primary-light/20">
      <aside className="w-72 hidden lg:flex flex-col p-6 space-y-6">
        <GlassCard className="flex items-center space-x-4 rtl:space-x-reverse">
          <div className="w-12 h-12 rounded-2xl bg-primary/60 flex items-center justify-center shadow-glass">
            <Bars3Icon className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide opacity-70">{settings?.storeName || "Salon"}</p>
            <h1 className="text-xl font-bold">Barber POS</h1>
          </div>
        </GlassCard>
        <nav className="space-y-3">
          {navLinks
            .filter((link) => !link.role || link.role === user?.role)
            .map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.to === "/"}
                className={({ isActive }) =>
                  `flex items-center space-x-3 rtl:space-x-reverse glass-button px-5 py-3 font-medium ${
                    isActive ? "bg-primary/60 text-white" : "text-gray-700"
                  }`
                }
              >
                <link.icon className="w-5 h-5" />
                <span>{t(link.labelKey)}</span>
              </NavLink>
            ))}
          {user?.role === "admin" && (
            <NavLink
              to="/users"
              className={({ isActive }) =>
                `flex items-center space-x-3 rtl:space-x-reverse glass-button px-5 py-3 font-medium ${
                  isActive ? "bg-primary/60 text-white" : "text-gray-700"
                }`
              }
            >
              <UsersIcon className="w-5 h-5" />
              <span>{t("users")}</span>
            </NavLink>
          )}
        </nav>
        <GlassButton className="mt-auto" onClick={logout}>
          {t("logout")}
        </GlassButton>
      </aside>
      <main className="flex-1 p-4 sm:p-8">
        <div className="lg:hidden mb-4">
          <GlassCard className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-wide opacity-60">{settings?.storeName}</p>
              <h1 className="text-xl font-bold">Barber POS</h1>
            </div>
            <GlassButton onClick={logout}>{t("logout")}</GlassButton>
          </GlassCard>
        </div>
        <GlassCard className="min-h-[calc(100vh-6rem)] p-6">
          <Outlet />
        </GlassCard>
      </main>
    </div>
  );
}
