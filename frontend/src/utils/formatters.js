import { format, formatDistanceToNow, isAfter, isBefore, addDays } from 'date-fns';

/**
 * Date and value formatting utilities used across the application.
 */

export const formatDate = (date) => {
  if (!date) return '—';
  return format(new Date(date), 'MMM dd, yyyy');
};

export const formatDateTime = (date) => {
  if (!date) return '—';
  return format(new Date(date), 'MMM dd, yyyy · h:mm a');
};

export const formatRelativeTime = (date) => {
  if (!date) return '—';
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const isExpiringSoon = (expiryDate, daysThreshold = 30) => {
  if (!expiryDate) return false;
  const expiry = new Date(expiryDate);
  const threshold = addDays(new Date(), daysThreshold);
  return isBefore(expiry, threshold) && isAfter(expiry, new Date());
};

export const isExpired = (expiryDate) => {
  if (!expiryDate) return false;
  return isBefore(new Date(expiryDate), new Date());
};

export const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let unitIndex = 0;
  let size = bytes;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '…';
};