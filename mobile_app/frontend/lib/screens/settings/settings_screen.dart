import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../providers/theme_provider.dart';
import '../../providers/auth_provider.dart';
import '../../services/local_storage_service.dart';
import '../../widgets/common/custom_card.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final themeProvider = context.watch<ThemeProvider>();
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // ─── Appearance ───
          _SectionHeader(title: 'Appearance')
              .animate()
              .fadeIn(duration: 300.ms),
          const Gap(8),
          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                // Theme toggle
                _SettingsTile(
                  icon: isDark ? Icons.dark_mode : Icons.light_mode,
                  iconColor: isDark
                      ? const Color(0xFFF59F00)
                      : AppTheme.brand600,
                  title: 'Dark Mode',
                  subtitle: isDark ? 'Enabled' : 'Disabled',
                  trailing: Switch.adaptive(
                    value: isDark,
                    onChanged: (_) => themeProvider.toggleTheme(),
                    activeColor: AppTheme.brand600,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

          const Gap(24),

          // ─── Security ───
          _SectionHeader(title: 'Security')
              .animate()
              .fadeIn(delay: 150.ms, duration: 300.ms),
          const Gap(8),
          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.fingerprint,
                  iconColor: const Color(0xFF20C997),
                  title: 'Biometric Login',
                  subtitle: authProvider.isBiometricEnabled
                      ? 'Fingerprint / Face ID enabled'
                      : 'Disabled',
                  trailing: authProvider.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Switch.adaptive(
                          value: authProvider.isBiometricEnabled,
                          onChanged: (_) => authProvider.toggleBiometric(),
                          activeColor: AppTheme.brand600,
                        ),
                ),
                _divider(theme),
                _SettingsTile(
                  icon: Icons.lock_clock,
                  iconColor: const Color(0xFF7C4DFF),
                  title: 'Auto-Lock',
                  subtitle: 'Lock after 5 minutes of inactivity',
                  trailing: Switch.adaptive(
                    value: LocalStorageService.autoLockEnabled,
                    onChanged: (val) {
                      LocalStorageService.setAutoLockEnabled(val);
                      (context as Element).markNeedsBuild();
                    },
                    activeColor: AppTheme.brand600,
                  ),
                ),
                _divider(theme),
                _SettingsTile(
                  icon: Icons.lock_outline,
                  iconColor: const Color(0xFFF59F00),
                  title: 'Change Password',
                  onTap: () => _showChangePasswordDialog(context),
                  trailing: Icon(
                    Icons.chevron_right,
                    color: theme.colorScheme.onSurface.withOpacity(0.3),
                    size: 20,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

          const Gap(24),

          // ─── Storage ───
          _SectionHeader(title: 'Storage & Data')
              .animate()
              .fadeIn(delay: 250.ms, duration: 300.ms),
          const Gap(8),
          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.storage_outlined,
                  iconColor: AppTheme.brand600,
                  title: 'Offline Storage',
                  subtitle: 'Documents cached for offline viewing',
                  trailing: Text(
                    '24.5 MB',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                _divider(theme),
                _SettingsTile(
                  icon: Icons.cached,
                  iconColor: const Color(0xFFFA5252),
                  title: 'Clear Cache',
                  subtitle: 'Free up storage space',
                  onTap: () => _showClearCacheDialog(context),
                  trailing: Icon(
                    Icons.chevron_right,
                    color: theme.colorScheme.onSurface.withOpacity(0.3),
                    size: 20,
                  ),
                ),
                _divider(theme),
                _SettingsTile(
                  icon: Icons.download_outlined,
                  iconColor: const Color(0xFF20C997),
                  title: 'Auto-Download',
                  subtitle: 'Download docs for offline access',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (_) {},
                    activeColor: AppTheme.brand600,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

          const Gap(24),

          // ─── Notifications ───
          _SectionHeader(title: 'Notifications')
              .animate()
              .fadeIn(delay: 350.ms, duration: 300.ms),
          const Gap(8),
          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.notifications_outlined,
                  iconColor: const Color(0xFF339AF0),
                  title: 'Push Notifications',
                  subtitle: 'Receive alerts and updates',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (_) {},
                    activeColor: AppTheme.brand600,
                  ),
                ),
                _divider(theme),
                _SettingsTile(
                  icon: Icons.schedule_outlined,
                  iconColor: const Color(0xFFF59F00),
                  title: 'Expiry Reminders',
                  subtitle: 'Get notified before documents expire',
                  trailing: Switch.adaptive(
                    value: true,
                    onChanged: (_) {},
                    activeColor: AppTheme.brand600,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

          const Gap(32),

          // ─── App Info ───
          Center(
            child: Column(
              children: [
                Text(
                  'DocIntel',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                  ),
                ),
                const Gap(2),
                Text(
                  'Version 1.0.0',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.3),
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 500.ms, duration: 400.ms),

          const Gap(20),
        ],
      ),
    );
  }

  Widget _divider(ThemeData theme) {
    return Divider(
      height: 1,
      indent: 56,
      color: theme.colorScheme.onSurface.withOpacity(0.06),
    );
  }

  void _showChangePasswordDialog(BuildContext context) {
    final currentPasswordController = TextEditingController();
    final newPasswordController = TextEditingController();
    final confirmPasswordController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Change Password'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: currentPasswordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Current Password',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: newPasswordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'New Password',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: confirmPasswordController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: 'Confirm New Password',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              if (newPasswordController.text != confirmPasswordController.text) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: const Text('Passwords do not match'),
                    backgroundColor: const Color(0xFFFA5252),
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                );
                return;
              }
              final auth = context.read<AuthProvider>();
              final success = await auth.changePassword(
                currentPasswordController.text,
                newPasswordController.text,
              );
              if (ctx.mounted) {
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success
                        ? 'Password changed successfully'
                        : auth.error ?? 'Failed to change password'),
                    backgroundColor:
                        success ? const Color(0xFF20C997) : const Color(0xFFFA5252),
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                );
              }
            },
            child: const Text('Change'),
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Clear Cache'),
        content: const Text(
            'This will remove all cached data and offline documents. You will need to re-download them.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: const Text('Cache cleared successfully'),
                  backgroundColor: const Color(0xFF20C997),
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              );
            },
            child: const Text(
              'Clear',
              style: TextStyle(color: Color(0xFFFA5252)),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Text(
      title.toUpperCase(),
      style: theme.textTheme.bodySmall?.copyWith(
        color: theme.colorScheme.onSurface.withOpacity(0.4),
        fontWeight: FontWeight.w600,
        letterSpacing: 1.2,
        fontSize: 11,
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String? subtitle;
  final Widget? trailing;
  final VoidCallback? onTap;

  const _SettingsTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    this.subtitle,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return ListTile(
      onTap: onTap,
      leading: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: isDark
              ? iconColor.withOpacity(0.12)
              : iconColor.withOpacity(0.08),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: iconColor, size: 20),
      ),
      title: Text(
        title,
        style: theme.textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle!,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.4),
                fontSize: 12,
              ),
            )
          : null,
      trailing: trailing,
    );
  }
}
