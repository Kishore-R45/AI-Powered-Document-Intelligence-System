enum NotificationType { expiry, upload, system, security }

class NotificationModel {
  final String id;
  final String title;
  final String body;
  final NotificationType type;
  final bool isRead;
  final DateTime createdAt;
  final String? documentId;
  final String? actionRoute;

  const NotificationModel({
    required this.id,
    required this.title,
    required this.body,
    required this.type,
    this.isRead = false,
    required this.createdAt,
    this.documentId,
    this.actionRoute,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      body: json['message'] ?? json['body'] ?? '',
      type: _parseType(json['type']),
      isRead: json['read'] ?? json['isRead'] ?? false,
      createdAt: json['createdAt'] != null
          ? (DateTime.tryParse(json['createdAt'])?.toLocal() ?? DateTime.now())
          : DateTime.now(),
      documentId: json['documentId'],
      actionRoute: json['actionRoute'],
    );
  }

  static NotificationType _parseType(dynamic type) {
    if (type == null) return NotificationType.system;
    final t = type.toString().toLowerCase();
    if (t.contains('expir')) return NotificationType.expiry;
    if (t.contains('upload') || t.contains('delete')) return NotificationType.upload;
    if (t.contains('secur') || t.contains('login')) return NotificationType.security;
    return NotificationType.system;
  }

  NotificationModel copyWith({
    String? id,
    String? title,
    String? body,
    NotificationType? type,
    bool? isRead,
    DateTime? createdAt,
    String? documentId,
    String? actionRoute,
  }) {
    return NotificationModel(
      id: id ?? this.id,
      title: title ?? this.title,
      body: body ?? this.body,
      type: type ?? this.type,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt ?? this.createdAt,
      documentId: documentId ?? this.documentId,
      actionRoute: actionRoute ?? this.actionRoute,
    );
  }
}
