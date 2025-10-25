import { useForm } from "react-hook-form";
import { useAuth } from "../contexts/AuthContext";
import GlassCard from "../components/ui/GlassCard";
import GlassButton from "../components/ui/GlassButton";
import { useTranslation } from "react-i18next";

interface LoginForm {
  username: string;
  password: string;
}

export default function LoginPage() {
  const { register, handleSubmit } = useForm<LoginForm>({
    defaultValues: { username: "admin", password: "password" }
  });
  const { login, loading } = useAuth();
  const { t } = useTranslation();

  const onSubmit = handleSubmit(async (values) => {
    await login(values.username, values.password);
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-light/40 to-accent/60">
      <GlassCard className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-primary-dark mb-2">{t("welcomeBack")}</h1>
          <p className="text-sm text-gray-600">Barber POS Suite</p>
        </div>
        <form className="space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">{t("username")}</label>
            <input className="neu-input w-full" placeholder="admin" {...register("username", { required: true })} />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-gray-700">{t("password")}</label>
            <input type="password" className="neu-input w-full" placeholder="••••••" {...register("password", { required: true })} />
          </div>
          <GlassButton type="submit" className="w-full justify-center" disabled={loading}>
            {loading ? "..." : t("login")}
          </GlassButton>
        </form>
      </GlassCard>
    </div>
  );
}
