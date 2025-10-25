import { useEffect, useState } from "react";
import PageHeader from "../components/PageHeader";
import GlassCard from "../components/ui/GlassCard";
import GlassButton from "../components/ui/GlassButton";
import { useSettings } from "../contexts/SettingsContext";
import { useToast } from "../hooks/useToast";

export default function SettingsPage() {
  const { settings, saveSettings, refreshSettings } = useSettings();
  const [draft, setDraft] = useState(settings);
  const toast = useToast();

  useEffect(() => {
    setDraft(settings);
  }, [settings]);

  const handleSave = async () => {
    if (!draft) return;
    await saveSettings(draft);
    toast.success("تم حفظ الإعدادات");
    refreshSettings();
  };

  const handleUploadLogo = async () => {
    const result = await window.posAPI.uploadLogo();
    if (result.success) {
      toast.success("تم تحديث الشعار");
      refreshSettings();
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader title="الإعدادات" description="تهيئة النظام حسب هوية المتجر" />
      {draft && (
        <GlassCard className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-semibold">اسم المتجر</label>
            <input className="neu-input" value={draft.storeName} onChange={(event) => setDraft({ ...draft, storeName: event.target.value })} />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">اللغة</label>
            <select className="neu-input" value={draft.language} onChange={(event) => setDraft({ ...draft, language: event.target.value as "ar" | "en" })}>
              <option value="ar">العربية</option>
              <option value="en">English</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">العملة</label>
            <input className="neu-input" value={draft.currency} onChange={(event) => setDraft({ ...draft, currency: event.target.value })} />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">نسبة الضريبة</label>
            <input type="number" className="neu-input" value={draft.taxRate} step={0.01} onChange={(event) => setDraft({ ...draft, taxRate: Number(event.target.value) })} />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">نوع الطباعة</label>
            <select className="neu-input" value={draft.receiptType} onChange={(event) => setDraft({ ...draft, receiptType: event.target.value as "thermal" | "a4" })}>
              <option value="thermal">إيصال حراري</option>
              <option value="a4">A4</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold">الشعار</label>
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              {draft.logoPath && <img src={draft.logoPath} alt="Logo" className="w-16 h-16 rounded-2xl object-cover shadow-glass" />}
              <GlassButton onClick={handleUploadLogo}>تحميل شعار</GlassButton>
            </div>
          </div>
          <div className="md:col-span-2 flex justify-end">
            <GlassButton onClick={handleSave}>حفظ الإعدادات</GlassButton>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
