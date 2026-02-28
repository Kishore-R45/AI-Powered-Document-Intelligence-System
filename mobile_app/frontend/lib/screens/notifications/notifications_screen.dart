import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../providers/notification_provider.dart';
import '../../widgets/notifications/notification_tile.dart';
import '../../widgets/common/empty_state.dart';
import '../../widgets/common/animated_list_item.dart';
import '../../models/notification_model.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<NotificationProvider>().fetchNotifications();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final provider = context.watch<NotificationProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        automaticallyImplyLeading: false,
        actions: [
          if (provider.unreadCount > 0)
            TextButton(
              onPressed: () async => await provider.markAllAsRead(),
              child: Text(
                'Mark all read',
                style: TextStyle(
                  color: AppTheme.brand600,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          const SizedBox(width: 4),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppTheme.brand600,
          unselectedLabelColor:
              theme.colorScheme.onSurface.withOpacity(0.4),
          indicatorColor: AppTheme.brand600,
          indicatorSize: TabBarIndicatorSize.label,
          labelStyle: const TextStyle(
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
          tabs: [
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('All'),
                  if (provider.notifications.isNotEmpty) ...[
                    const Gap(6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color: AppTheme.brand600.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${provider.notifications.length}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppTheme.brand600,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('Unread'),
                  if (provider.unreadCount > 0) ...[
                    const Gap(6),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 1),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFA5252).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        '${provider.unreadCount}',
                        style: const TextStyle(
                          fontSize: 11,
                          color: Color(0xFFFA5252),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const Tab(text: 'Expiry'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildNotificationList(provider.notifications, provider),
          _buildNotificationList(
            provider.notifications.where((n) => !n.isRead).toList(),
            provider,
          ),
          _buildNotificationList(
            provider.notifications
                .where((n) => n.type == NotificationType.expiry)
                .toList(),
            provider,
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationList(
      List<NotificationModel> notifications, NotificationProvider provider) {
    if (notifications.isEmpty) {
      return EmptyState(
        icon: Icons.notifications_none_rounded,
        title: 'All caught up!',
        subtitle: 'No notifications to show',
      );
    }

    return RefreshIndicator(
      color: AppTheme.brand600,
      onRefresh: () async => provider.fetchNotifications(),
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(vertical: 8),
        itemCount: notifications.length,
        itemBuilder: (context, index) {
          return AnimatedListItem(
            index: index,
            child: NotificationTile(
              notification: notifications[index],
              onTap: () async {
                await provider.markAsRead(notifications[index].id);
              },
              onDismiss: () async {
                await provider.deleteNotification(notifications[index].id);
              },
            ),
          );
        },
      ),
    );
  }
}
