import { useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react';
import { clsx } from 'clsx';

/**
 * Individual toast notification.
 * Auto-dismisses after a configurable duration.
 */
export default function Toast({ id, type = 'info', message, onDismiss, duration = 5000 }) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onDismiss(id), duration);
      return () => clearTimeout(timer);
    }
  }, [id, duration, onDismiss]);

  const config = {
    success: {
      icon: <CheckCircle size={20} />,
      styles: 'bg-success-50 border-success-500 text-success-700',
    },
    error: {
      icon: <XCircle size={20} />,
      styles: 'bg-error-50 border-error-500 text-error-700',
    },
    warning: {
      icon: <AlertTriangle size={20} />,
      styles: 'bg-warning-50 border-warning-500 text-warning-700',
    },
    info: {
      icon: <Info size={20} />,
      styles: 'bg-brand-50 border-brand-500 text-brand-700',
    },
  };

  const { icon, styles } = config[type] || config.info;

  return (
    <div
      className={clsx(
        'flex items-start gap-3 px-4 py-3 rounded-lg border-l-4 shadow-md animate-slide-down',
        styles
      )}
      role="alert"
    >
      <span className="shrink-0 mt-0.5">{icon}</span>
      <p className="text-sm font-medium flex-1">{message}</p>
      <button
        onClick={() => onDismiss(id)}
        className="shrink-0 p-0.5 rounded hover:bg-black/5 transition-colors"
        aria-label="Dismiss notification"
      >
        <X size={16} />
      </button>
    </div>
  );
}