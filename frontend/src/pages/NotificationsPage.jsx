import { Bell, CheckCheck } from 'lucide-react';
import Card from '../components/common/Card';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import Spinner from '../components/common/Spinner';
import useNotifications from '../hooks/useNotifications';
import { formatRelativeTime, formatDate } from '../utils/formatters';
import { AlertTriangle, Clock, Info } from 'lucide-react';
import { clsx } from 'clsx';

/**
 * Full notifications page.
 * Shows all notifications with ability to mark individual or all as read.
 */

const notificationIcons = {
  expiry_warning: AlertTriangle,
  expiry_reminder: Clock,
  info: Info,
};

const notificationColors = {
  expiry_warning: 'bg-warning-50 text-warning-500',
  expiry_reminder: 'bg-error-50 text-error-500',
  info: 'bg-brand-50 text-brand-500',
};

export default function NotificationsPage() {
  const { notifications, unreadCount, loading, markAsRead, markAllAsRead } =
    useNotifications();

  if (loading && notifications.length === 0) {
    return (
      <div className="flex items-center justify-center py-32">
        <Spinner size="xl" className="text-brand-600" />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="page-heading flex items-center gap-2">
            <Bell size={24} className="text-brand-600" />
            Notifications
          </h1>
          <p className="page-subheading">
            {unreadCount > 0
              ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`
              : 'You\'re all caught up'}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button
            variant="outline"
            size="sm"
            leftIcon={<CheckCheck size={16} />}
            onClick={markAllAsRead}
          >
            Mark All as Read
          </Button>
        )}
      </div>

      {/* Notification list */}
      {notifications.length === 0 ? (
        <Card>
          <EmptyState
            icon={Bell}
            title="No notifications yet"
            description="When you receive document expiry reminders or other updates, they will appear here."
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => {
            const Icon = notificationIcons[notification.type] || Info;
            const iconStyle = notificationColors[notification.type] || 'bg-neutral-100 text-neutral-500';

            return (
              <Card
                key={notification.id}
                hover
                padding="none"
                className={clsx(
                  'transition-all duration-200 cursor-pointer',
                  !notification.read && 'border-l-4 border-l-brand-500'
                )}
              >
                <div
                  className="flex items-start gap-4 p-5"
                  onClick={() => !notification.read && markAsRead(notification.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !notification.read) {
                      markAsRead(notification.id);
                    }
                  }}
                >
                  {/* Icon */}
                  <div
                    className={clsx(
                      'w-10 h-10 rounded-lg flex items-center justify-center shrink-0',
                      iconStyle
                    )}
                  >
                    <Icon size={20} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <h3
                        className={clsx(
                          'text-sm',
                          !notification.read
                            ? 'font-semibold text-neutral-900'
                            : 'font-medium text-neutral-700'
                        )}
                      >
                        {notification.title}
                      </h3>
                      <div className="flex items-center gap-2 shrink-0">
                        {!notification.read && (
                          <Badge variant="info" size="sm">New</Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-neutral-500 mt-1 leading-relaxed">
                      {notification.message}
                    </p>
                    <p className="text-xs text-neutral-400 mt-2">
                      {formatRelativeTime(notification.timestamp)}
                      {' · '}
                      {formatDate(notification.timestamp)}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}