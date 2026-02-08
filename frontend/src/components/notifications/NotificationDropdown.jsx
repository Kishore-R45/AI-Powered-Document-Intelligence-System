import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { NotificationContext } from '../../context/NotificationContext';
import NotificationItem from './NotificationItem';
import Button from '../common/Button';
import { ROUTES } from '../../utils/constants';
import { Bell } from 'lucide-react';

/**
 * Dropdown panel showing recent notifications.
 */
export default function NotificationDropdown({ onClose }) {
  const { notifications, markAsRead, markAllAsRead } = useContext(NotificationContext);
  const navigate = useNavigate();

  const recentNotifications = notifications.slice(0, 5);

  return (
    <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-neutral-200 rounded-xl shadow-lg z-50 animate-slide-down">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-100">
        <h3 className="text-sm font-semibold text-neutral-900">Notifications</h3>
        {notifications.some((n) => !n.read) && (
          <button
            onClick={markAllAsRead}
            className="text-xs font-medium text-brand-600 hover:text-brand-700 transition-colors"
          >
            Mark all read
          </button>
        )}
      </div>

      {/* Notifications list */}
      <div className="max-h-80 overflow-y-auto custom-scrollbar">
        {recentNotifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-neutral-400">
            <Bell size={24} className="mb-2" />
            <p className="text-sm">No notifications</p>
          </div>
        ) : (
          recentNotifications.map((notification) => (
            <NotificationItem
              key={notification.id}
              notification={notification}
              onMarkRead={() => markAsRead(notification.id)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      {notifications.length > 0 && (
        <div className="px-4 py-3 border-t border-neutral-100">
          <Button
            variant="ghost"
            size="sm"
            fullWidth
            onClick={() => {
              navigate(ROUTES.NOTIFICATIONS);
              onClose();
            }}
          >
            View all notifications
          </Button>
        </div>
      )}
    </div>
  );
}