import { createContext, useState, useEffect, useCallback, useMemo, useContext } from 'react';
import api from '../api/axios';
import ENDPOINTS from '../api/endpoints';
import { AuthContext } from './AuthContext';

/**
 * Notification context.
 * Fetches and manages user notifications and provides
 * unread count, mark-read, and mark-all-read functionality.
 *
 * Only fetches when the user is authenticated.
 * Polls for new notifications at a configurable interval.
 */
export const NotificationContext = createContext(null);

const POLL_INTERVAL = 60000; // 60 seconds

export function NotificationProvider({ children }) {
  const { isAuthenticated } = useContext(AuthContext);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);

  /**
   * Fetch notifications from the API.
   */
  const fetchNotifications = useCallback(async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      const response = await api.get(ENDPOINTS.NOTIFICATIONS.LIST);
      const data = response.data.notifications || response.data || [];
      setNotifications(data);
    } catch (error) {
      // Silent fail — notifications are non-critical
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  /**
   * Fetch on mount and set up polling when authenticated.
   */
  useEffect(() => {
    if (isAuthenticated) {
      fetchNotifications();

      const interval = setInterval(fetchNotifications, POLL_INTERVAL);
      return () => clearInterval(interval);
    } else {
      // Clear notifications on logout
      setNotifications([]);
    }
  }, [isAuthenticated, fetchNotifications]);

  /**
   * Mark a single notification as read.
   *
   * @param {string} notificationId
   */
  const markAsRead = useCallback(async (notificationId) => {
    // Optimistic update
    setNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
    );

    try {
      await api.patch(ENDPOINTS.NOTIFICATIONS.MARK_READ(notificationId));
    } catch (error) {
      // Revert on failure
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, read: false } : n))
      );
      console.error('Failed to mark notification as read:', error);
    }
  }, []);

  /**
   * Mark all notifications as read.
   */
  const markAllAsRead = useCallback(async () => {
    const previousState = [...notifications];

    // Optimistic update
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));

    try {
      await api.patch(ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ);
    } catch (error) {
      // Revert on failure
      setNotifications(previousState);
      console.error('Failed to mark all notifications as read:', error);
    }
  }, [notifications]);

  /**
   * Computed unread count.
   */
  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  );

  const value = useMemo(
    () => ({
      notifications,
      unreadCount,
      loading,
      markAsRead,
      markAllAsRead,
      refetch: fetchNotifications,
    }),
    [notifications, unreadCount, loading, markAsRead, markAllAsRead, fetchNotifications]
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}