import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/foundation.dart';

/// Top-level background message handler.
/// Must be a top-level or static function — cannot be anonymous or instance method.
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint('[FCM] Background message: ${message.messageId}');
}

/// Manages Firebase Cloud Messaging (FCM) push notifications.
/// 
/// Handles:
/// - Permission requests (Android 13+ POST_NOTIFICATIONS)
/// - FCM token retrieval & refresh
/// - Foreground notification display via flutter_local_notifications
/// - Background / terminated-app notification tap handling
class PushNotificationService {
  static final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  static bool _initialized = false;
  static String? _fcmToken;

  /// Current FCM registration token (null if not yet obtained).
  static String? get fcmToken => _fcmToken;

  /// Whether the service has been successfully initialized.
  static bool get isInitialized => _initialized;

  /// Callback invoked when the FCM token changes.
  /// The notification provider hooks into this to re-register with backend.
  static void Function(String token)? onTokenRefresh;

  // ─── Initialization ───

  /// Call once from main() after Firebase.initializeApp().
  static Future<void> initialize() async {
    if (_initialized) return;

    try {
      // 1. Request notification permission (required on Android 13+ / iOS)
      final settings = await _messaging.requestPermission(
        alert: true,
        announcement: false,
        badge: true,
        carPlay: false,
        criticalAlert: false,
        provisional: false,
        sound: true,
      );

      if (settings.authorizationStatus != AuthorizationStatus.authorized &&
          settings.authorizationStatus != AuthorizationStatus.provisional) {
        debugPrint('[FCM] Notification permission denied');
        return;
      }

      // 2. Create Android notification channel (required for Android 8+)
      const channel = AndroidNotificationChannel(
        'infovault_notifications', // must match backend channel_id
        'InfoVault Notifications',
        description: 'Document updates, expiry reminders & more',
        importance: Importance.high,
        playSound: true,
        enableVibration: true,
        showBadge: true,
      );

      await _localNotifications
          .resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>()
          ?.createNotificationChannel(channel);

      // 3. Initialize local notifications plugin (for foreground display)
      const androidInit =
          AndroidInitializationSettings('@mipmap/ic_launcher');
      const initSettings = InitializationSettings(android: androidInit);
      await _localNotifications.initialize(
        initSettings,
        onDidReceiveNotificationResponse: _onNotificationTap,
      );

      // 4. Listen for foreground FCM messages
      FirebaseMessaging.onMessage.listen(_showForegroundNotification);

      // 5. Listen for notification taps (app was in background)
      FirebaseMessaging.onMessageOpenedApp.listen(_onRemoteMessageTap);

      // 6. Check if app was launched from a notification tap
      final initialMessage = await _messaging.getInitialMessage();
      if (initialMessage != null) {
        _onRemoteMessageTap(initialMessage);
      }

      // 7. Retrieve FCM token
      _fcmToken = await _messaging.getToken();
      debugPrint('[FCM] Token obtained: ${_fcmToken?.substring(0, 20)}...');

      // 8. Listen for token refreshes
      _messaging.onTokenRefresh.listen((newToken) {
        _fcmToken = newToken;
        debugPrint('[FCM] Token refreshed');
        onTokenRefresh?.call(newToken);
      });

      // 9. iOS foreground presentation options (good practice)
      await _messaging.setForegroundNotificationPresentationOptions(
        alert: true,
        badge: true,
        sound: true,
      );

      _initialized = true;
      debugPrint('[FCM] Push notification service initialized');
    } catch (e) {
      debugPrint('[FCM] Initialization error: $e');
    }
  }

  // ─── Foreground Notification Display ───

  /// Shows a local notification when a message arrives while the app is open.
  static void _showForegroundNotification(RemoteMessage message) {
    final notification = message.notification;
    if (notification == null) return;

    _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'infovault_notifications',
          'InfoVault Notifications',
          channelDescription: 'Document updates, expiry reminders & more',
          importance: Importance.high,
          priority: Priority.high,
          icon: '@mipmap/ic_launcher',
          playSound: true,
          enableVibration: true,
          showWhen: true,
        ),
      ),
      payload: message.data['type'],
    );
  }

  // ─── Notification Tap Handlers ───

  /// User tapped a local (foreground) notification.
  static void _onNotificationTap(NotificationResponse response) {
    debugPrint('[FCM] Notification tapped: ${response.payload}');
    // Navigation can be handled through a global navigator key if needed
  }

  /// User tapped a push notification that launched/resumed the app.
  static void _onRemoteMessageTap(RemoteMessage message) {
    debugPrint('[FCM] Remote message tapped: ${message.data}');
    // Navigation can be handled through a global navigator key if needed
  }
}
