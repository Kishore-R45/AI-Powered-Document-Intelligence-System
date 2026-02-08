import { clsx } from 'clsx';
import { AlertTriangle, Clock, Info } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

/**
 * Individual notification item.
 *
 * @param {object} notification - { id, type, title, message, timestamp, read }
 * @param {function} onMarkRead
 */
const notificationIcons = {
  expiry_warning: AlertTriangle,
  expiry_reminder: Clock,
  info: Info,
};

const notificationColors = {
  expiry_warning: 'text-warning-500',
  expiry_reminder: 'text-error-500',
  info: 'text-brand-500',
};

export default function NotificationItem({ notification, onMarkRead }) {
  const Icon = notificationIcons[notification.type] || Info;
  const iconColor = notificationColors[notification.type] || 'text-neutral-500';

  return (
    <div
      className={clsx(
        'flex items-start gap-3 px-4 py-3 hover:bg-neutral-25 transition-colors cursor-pointer',
        !notification.read && 'bg-brand-50/30'
      )}
      onClick={onMarkRead}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter') onMarkRead();
      }}
    >
      <Icon size={18} className={clsx('shrink-0 mt-0.5', iconColor)} />
      <div className="flex-1 min-w-0">
        <p className={clsx('text-sm', !notification.read ? 'font-semibold text-neutral-900' : 'font-medium text-neutral-700')}>
          {notification.title}
        </p>
        <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">{notification.message}</p>
        <p className="text-xs text-neutral-400 mt-1">{formatRelativeTime(notification.timestamp)}</p>
      </div>
      {!notification.read && (
        <span className="w-2 h-2 bg-brand-500 rounded-full shrink-0 mt-1.5" />
      )}
    </div>
  );
}