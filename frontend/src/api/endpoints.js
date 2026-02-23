/**
 * Centralized API endpoint definitions.
 * Keeps all route strings in one place for maintainability.
 */
const ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    SIGNUP: '/auth/signup',
    VERIFY_OTP: '/auth/verify-otp',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    FORGOT_PASSWORD: '/auth/forgot-password',
    VERIFY_RESET_OTP: '/auth/verify-reset-otp',
    RESET_PASSWORD: '/auth/reset-password',
  },
  DOCUMENTS: {
    UPLOAD: '/documents/upload',
    LIST: '/documents/list',
    DELETE: (id) => `/documents/delete/${id}`,
    DETAILS: (id) => `/documents/${id}`,
  },
  CHAT: {
    QUERY: '/chat/query',
    HISTORY: '/chat/history',
  },
  USER: {
    PROFILE: '/user/profile',
    CHANGE_PASSWORD: '/user/change-password',
    LOGOUT_ALL: '/user/logout-all',
  },
  NOTIFICATIONS: {
    LIST: '/notifications',
    MARK_READ: (id) => `/notifications/${id}/read`,
    MARK_ALL_READ: '/notifications/read-all',
  },
  DASHBOARD: {
    STATS: '/dashboard/stats',
  },
};

export default ENDPOINTS;