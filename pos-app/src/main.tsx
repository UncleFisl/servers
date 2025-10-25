import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import App from "./App";
import "./styles/globals.css";
import "./i18n";
import { AuthProvider } from "./contexts/AuthContext";
import { SettingsProvider } from "./contexts/SettingsContext";
import { ToastProvider } from "./contexts/ToastContext";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <HashRouter>
      <ToastProvider>
        <SettingsProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </SettingsProvider>
      </ToastProvider>
    </HashRouter>
  </React.StrictMode>
);
