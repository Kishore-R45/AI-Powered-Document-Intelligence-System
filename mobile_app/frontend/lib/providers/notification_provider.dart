import 'package:flutter/material.dart';
import '../models/notification_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';

class NotificationProvider extends ChangeNotifier {
  List<NotificationModel> _notifications = [];
  bool _isLoading = false;
  String _filter = 'All'; // 'All', 'Unread', 'Expiry'
  String? _fcmToken;

  // Getters
  List<NotificationModel> get notifications => _filteredNotifications;
  bool get isLoading => _isLoading;
  String get filter => _filter;

  int get unreadCount =>
      _notifications.where((n) => !n.isRead).length;

  List<NotificationModel> get _filteredNotifications {
    switch (_filter) {
      case 'Unread':
        return _notifications.where((n) => !n.isRead).toList();
      case 'Expiry':
        return _notifications
            .where((n) => n.type == NotificationType.expiry)
            .toList();
      default:
        return _notifications;
    }
  }

  Future<void> fetchNotifications() async {
    _isLoading = true;
    notifyListeners();

    final res = await ApiClient.get(Endpoints.notifications);

    if (res.success && res.data?['notifications'] != null) {
      final list = res.data!['notifications'] as List;
      _notifications = list
          .map((n) => NotificationModel.fromJson(n as Map<String, dynamic>))
          .toList();
    }
    _isLoading = false;
    notifyListeners();
  }

  void setFilter(String filter) {
    _filter = filter;
    notifyListeners();
  }

  Future<void> markAsRead(String id) async {
    final res = await ApiClient.post(Endpoints.notificationRead(id));
    if (res.success) {
      final index = _notifications.indexWhere((n) => n.id == id);
      if (index != -1) {
        _notifications[index] = _notifications[index].copyWith(isRead: true);
        notifyListeners();
      }
    }
  }

  Future<void> markAllAsRead() async {
    final res = await ApiClient.post(Endpoints.notificationsReadAll);
    if (res.success) {
      _notifications = _notifications
          .map((n) => n.copyWith(isRead: true))
          .toList();
      notifyListeners();
    }
  }

  Future<void> deleteNotification(String id) async {
    final res = await ApiClient.delete(Endpoints.notificationDelete(id));
    if (res.success) {
      _notifications.removeWhere((n) => n.id == id);
      notifyListeners();
    }
  }

  // ─── FCM Token Management ───

  /// Register an FCM token with the backend for push notifications.
  Future<bool> registerFcmToken(String token) async {
    _fcmToken = token;
    final res = await ApiClient.post(
      Endpoints.registerFcm,
      body: {'fcmToken': token},
    );
    return res.success;
  }

  /// Unregister the FCM token (e.g. on logout).
  Future<bool> unregisterFcmToken() async {
    if (_fcmToken == null) return true;
    final res = await ApiClient.post(
      Endpoints.unregisterFcm,
      body: {'fcmToken': _fcmToken},
    );
    if (res.success) _fcmToken = null;
    return res.success;
  }
}
