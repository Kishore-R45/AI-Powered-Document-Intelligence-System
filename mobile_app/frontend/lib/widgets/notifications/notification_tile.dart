import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../config/theme.dart';
import '../../models/notification_model.dart';

class NotificationTile extends StatelessWidget {
  final NotificationModel notification;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;

  const NotificationTile({
    super.key,
    required this.notification,
    this.onTap,
    this.onDismiss,
  });

  IconData _getIcon() {
    switch (notification.type) {
      case NotificationType.expiry:
        return Icons.timer_outlined;
      case NotificationType.upload:
        return Icons.cloud_upload_outlined;
      case NotificationType.system:
        return Icons.info_outlined;
      case NotificationType.security:
        return Icons.shield_outlined;
    }
  }

  Color _getIconColor() {
    switch (notification.type) {
      case NotificationType.expiry:
        return AppTheme.warning500;
      case NotificationType.upload:
        return AppTheme.success500;
      case NotificationType.system:
        return AppTheme.brand600;
      case NotificationType.security:
        return AppTheme.error500;
    }
  }

  Color _getIconBgColor(bool isDark) {
    switch (notification.type) {
      case NotificationType.expiry:
        return isDark ? AppTheme.warning700.withOpacity(0.2) : AppTheme.warning50;
      case NotificationType.upload:
        return isDark ? AppTheme.success700.withOpacity(0.2) : AppTheme.success50;
      case NotificationType.system:
        return isDark ? AppTheme.brand900.withOpacity(0.3) : AppTheme.brand50;
      case NotificationType.security:
        return isDark ? AppTheme.error700.withOpacity(0.2) : AppTheme.error50;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) return 'Just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return DateFormat('MMM d').format(time);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final iconColor = _getIconColor();
    final iconBgColor = _getIconBgColor(isDark);

    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismiss?.call(),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: AppTheme.error500,
        child: const Icon(Icons.delete_outlined, color: Colors.white),
      ),
      child: InkWell(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            color: notification.isRead
                ? Colors.transparent
                : (isDark
                    ? AppTheme.brand900.withOpacity(0.1)
                    : AppTheme.brand50.withOpacity(0.5)),
            border: Border(
              bottom: BorderSide(
                color: isDark
                    ? const Color(0xFF2D3050)
                    : AppTheme.neutral200,
                width: 0.5,
              ),
            ),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: iconBgColor,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(_getIcon(), size: 20, color: iconColor),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            notification.title,
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  fontWeight: notification.isRead
                                      ? FontWeight.w500
                                      : FontWeight.w600,
                                ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (!notification.isRead)
                          Container(
                            width: 8,
                            height: 8,
                            decoration: const BoxDecoration(
                              color: AppTheme.brand600,
                              shape: BoxShape.circle,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      notification.body,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withOpacity(0.6),
                            height: 1.4,
                          ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _formatTime(notification.createdAt),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withOpacity(0.4),
                            fontSize: 11,
                          ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
