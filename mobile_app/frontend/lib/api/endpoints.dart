/// All backend API endpoint paths.
/// These map to the Flask routes in the backend.
class Endpoints {
  Endpoints._();

  // ─── Auth ───
  static const String signup = '/auth/signup';
  static const String verifyOtp = '/auth/verify-otp';
  static const String login = '/auth/login';
  static const String logout = '/auth/logout';
  static const String refresh = '/auth/refresh';
  static const String forgotPassword = '/auth/forgot-password';
  static const String verifyResetOtp = '/auth/verify-reset-otp';
  static const String resetPassword = '/auth/reset-password';

  // ─── Documents ───
  static const String documentUpload = '/documents/upload';
  static const String documentList = '/documents/list';
  static String documentGet(String id) => '/documents/$id';
  static String documentView(String id) => '/documents/$id/view';
  static String documentDelete(String id) => '/documents/delete/$id';
  static String documentUpdate(String id) => '/documents/$id';
  static String documentReindex(String id) => '/documents/$id/reindex';

  // ─── Chat ───
  static const String chatQuery = '/chat/query';
  static const String chatHistory = '/chat/history';

  // ─── Dashboard ───
  static const String dashboardStats = '/dashboard/stats';
  static const String dashboardExpiring = '/dashboard/expiring';
  static const String dashboardExpired = '/dashboard/expired';
  static const String dashboardTimeline = '/dashboard/timeline';

  // ─── Notifications ───
  static const String notifications = '/notifications';
  static String notificationRead(String id) => '/notifications/$id/read';
  static const String notificationsReadAll = '/notifications/read-all';
  static String notificationDelete(String id) => '/notifications/$id';
  static const String notificationsUnreadCount = '/notifications/unread-count';

  // ─── User ───
  static const String userProfile = '/user/profile';
  static const String userChangePassword = '/user/change-password';
  static const String userLogoutAll = '/user/logout-all';
}
