import { useToastContext } from "../contexts/ToastContext";

export function useToast() {
  const { push } = useToastContext();

  return {
    success: (title: string, description?: string) => push({ type: "success", title, description }),
    error: (title: string, description?: string) => push({ type: "error", title, description }),
    info: (title: string, description?: string) => push({ type: "info", title, description })
  };
}
