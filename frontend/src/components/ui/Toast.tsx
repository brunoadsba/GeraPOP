import { useCallback, useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { IconCheckCircle, IconAlertCircle, IconInfo, IconX } from './Icons';

export type ToastVariant = 'success' | 'error' | 'info';

interface ToastItem {
  id: number;
  message: ReactNode;
  variant: ToastVariant;
  exiting?: boolean;
}

let toastCounter = 0;
const listeners: Array<(t: ToastItem) => void> = [];

/** Imperatively show a toast from anywhere. */
export function showToast(message: ReactNode, variant: ToastVariant = 'info') {
  const item: ToastItem = { id: ++toastCounter, message, variant };
  listeners.forEach((fn) => fn(item));
}

const AUTO_DISMISS_MS = 4000;
const EXIT_MS = 300;

const ICONS: Record<ToastVariant, ReactNode> = {
  success: <IconCheckCircle size={18} />,
  error: <IconAlertCircle size={18} />,
  info: <IconInfo size={18} />,
};

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const timers = useRef<Map<number, ReturnType<typeof setTimeout>>>(new Map());

  const dismiss = useCallback((id: number) => {
    setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)));
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, EXIT_MS);
  }, []);

  useEffect(() => {
    const handler = (item: ToastItem) => {
      setToasts((prev) => [...prev, item]);
      const timer = setTimeout(() => dismiss(item.id), AUTO_DISMISS_MS);
      timers.current.set(item.id, timer);
    };
    listeners.push(handler);
    return () => {
      const idx = listeners.indexOf(handler);
      if (idx >= 0) listeners.splice(idx, 1);
      timers.current.forEach(clearTimeout);
    };
  }, [dismiss]);

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.variant}${t.exiting ? ' toast-exit' : ''}`}>
          <span className="toast-icon">{ICONS[t.variant]}</span>
          <span className="toast-msg">{t.message}</span>
          <button
            className="toast-close"
            onClick={() => dismiss(t.id)}
            aria-label="Fechar notificação"
          >
            <IconX size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
