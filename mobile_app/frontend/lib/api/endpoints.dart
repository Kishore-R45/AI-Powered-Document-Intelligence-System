/// All backend API endpoint paths.
/// These map to the Flask routes in the mobile backend.
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

  // Mobile-specific auth
  static const String biometricLogin = '/auth/biometric-login';
  static const String registerDevice = '/auth/register-device';
  static const String validateSession = '/auth/validate-session';

  // ─── Documents ───
  static const String documentUpload = '/documents/upload';
  static const String documentList = '/documents/list';
  static String documentGet(String id) => '/documents/$id';
  static String documentDelete(String id) => '/documents/delete/$id';
  static String documentUpdate(String id) => '/documents/$id';
  static String documentExtractedData(String id) => '/documents/$id/extracted-data';
  static String documentReExtract(String id) => '/documents/$id/re-extract';
  static String documentDeleteField(String id) => '/documents/$id/extracted-data/delete-field';
  static String documentUpdateField(String id) => '/documents/$id/extracted-data/update-field';
  static String documentDeleteFields(String id) => '/documents/$id/extracted-data/delete-fields';
  static const String documentReindex = '/documents/reindex';

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
  static const String registerFcm = '/notifications/register-fcm';
  static const String unregisterFcm = '/notifications/unregister-fcm';
  static const String testPush = '/notifications/test-push';

  // ─── User ───
  static const String userProfile = '/user/profile';
  static const String userChangePassword = '/user/change-password';
  static const String userLogoutAll = '/user/logout-all';

  // Mobile-specific user
  static const String biometricToggle = '/user/biometric/toggle';
  static const String biometricStatus = '/user/biometric/status';
  static const String userSessions = '/user/sessions';
  static String revokeSession(String id) => '/user/sessions/$id';
  static const String trustedDevices = '/user/trusted-devices';
  static String revokeTrustedDevice(String id) => '/user/trusted-devices/$id';
}
