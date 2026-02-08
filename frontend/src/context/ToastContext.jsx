import { createContext, useState, useCallback, useMemo } from 'react';
import Toast from '../components/common/Toast';

/**
 * Toast notification context.
 * Provides methods to show success, error, warning, and info toasts.
 * Renders toast container at the top-right of the viewport.
 */
export const ToastContext = createContext(null);

let toastIdCounter = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  /**
   * Remove a toast by its ID.
   */
  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  /**
   * Add a new toast notification.
   *
   * @param {'success'|'error'|'warning'|'info'} type
   * @param {string} message
   * @param {number} duration - Auto-dismiss time in ms (0 = no auto-dismiss)
   */
  const addToast = useCallback((type, message, duration = 5000) => {
    const id = ++toastIdCounter;
    setToasts((prev) => [...prev, { id, type, message, duration }]);
    return id;
  }, []);

  /**
   * Convenience methods for each toast type.
   */
  const toast = useMemo(
    () => ({
      success: (message, duration) => addToast('success', message, duration),
      error: (message, duration) => addToast('error', message, duration),
      warning: (message, duration) => addToast('warning', message, duration),
      info: (message, duration) => addToast('info', message, duration),
    }),
    [addToast]
  );

  const value = useMemo(() => ({ toast }), [toast]);

  return (
    <ToastContext.Provider value={value}>
      {children}

      {/* Toast container — fixed top-right */}
      {toasts.length > 0 && (
        <div
          className="fixed top-4 right-4 z-[100] flex flex-col gap-3 w-full max-w-sm pointer-events-none"
          aria-live="polite"
          aria-label="Notifications"
        >
          {toasts.map((t) => (
            <div key={t.id} className="pointer-events-auto">
              <Toast
                id={t.id}
                type={t.type}
                message={t.message}
                duration={t.duration}
                onDismiss={dismissToast}
              />
            </div>
          ))}
        </div>
      )}
    </ToastContext.Provider>
  );
}