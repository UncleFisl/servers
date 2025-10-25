import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

export interface Settings {
  id?: number;
  language: "ar" | "en";
  currency: string;
  taxRate: number;
  storeName: string;
  logoPath?: string | null;
  receiptType: "thermal" | "a4";
}

interface SettingsContextValue {
  settings: Settings | null;
  refreshSettings: () => Promise<void>;
  saveSettings: (settings: Settings) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextValue | undefined>(undefined);

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<Settings | null>(null);

  const refreshSettings = useCallback(async () => {
    const data = await window.posAPI.getSettings();
    setSettings(
      data || {
        language: "ar",
        currency: "SAR",
        taxRate: 0.15,
        storeName: "صالون الأناقة",
        logoPath: null,
        receiptType: "thermal"
      }
    );
  }, []);

  useEffect(() => {
    refreshSettings();
  }, [refreshSettings]);

  const saveSettings = useCallback(async (values: Settings) => {
    await window.posAPI.saveSettings(values);
    await refreshSettings();
  }, [refreshSettings]);

  const value = useMemo(
    () => ({ settings, refreshSettings, saveSettings }),
    [settings, refreshSettings, saveSettings]
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return context;
}
