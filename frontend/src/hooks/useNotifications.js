import { useContext } from 'react';
import { NotificationContext } from '../context/NotificationContext';

/**
 * Convenience hook for accessing notification context.
 * Throws if used outside of NotificationProvider.
 *
 * @returns {{
 *   notifications: Array,
 *   unreadCount: number,
 *   loading: boolean,
 *   markAsRead: (id: string) => Promise,
 *   markAllAsRead: () => Promise,
 *   refetch: () => Promise,
 * }}
 */
export default function useNotifications() {
  const context = useContext(NotificationContext);

  if (!context) {
    throw new Error(
      'useNotifications must be used within a NotificationProvider. ' +
      'Wrap your component tree with <NotificationProvider>.'
    );
  }

  return context;
}