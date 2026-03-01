import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/document_provider.dart';
import '../../widgets/common/custom_card.dart';
import '../../widgets/common/custom_button.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final auth = context.watch<AuthProvider>();
    final docs = context.watch<DocumentProvider>();
    final user = auth.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            onPressed: () => Navigator.pushNamed(context, '/settings'),
            icon: const Icon(Icons.settings_outlined, size: 22),
          ),
          const SizedBox(width: 4),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // ─── Profile Avatar & Info ───
            Center(
              child: Column(
                children: [
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [AppTheme.brand600, AppTheme.brand400],
                      ),
                      shape: BoxShape.circle,
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.brand600.withOpacity(0.3),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: Center(
                      child: Text(
                        user?.initials ?? 'U',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 36,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ),
                  )
                      .animate()
                      .fadeIn(duration: 500.ms)
                      .scale(begin: const Offset(0.8, 0.8)),

                  const Gap(16),

                  Text(
                    user?.name ?? 'User',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ).animate().fadeIn(delay: 100.ms),

                  const Gap(4),

                  Text(
                    user?.email ?? '',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.5),
                    ),
                  ).animate().fadeIn(delay: 150.ms),
                ],
              ),
            ),

            const Gap(32),

            // ─── Stats Cards ───
            Row(
              children: [
                Expanded(
                  child: _StatCard(
                    label: 'Documents',
                    value: '${docs.documents.length}',
                    icon: Icons.description_outlined,
                    color: AppTheme.brand600,
                  ),
                ),
                const Gap(12),
                Expanded(
                  child: _StatCard(
                    label: 'Categories',
                    value: '${docs.documents.map((d) => d.category).toSet().length}',
                    icon: Icons.category_outlined,
                    color: const Color(0xFF7C4DFF),
                  ),
                ),
                const Gap(12),
                Expanded(
                  child: _StatCard(
                    label: 'Storage',
                    value: _calcStorage(docs),
                    icon: Icons.cloud_outlined,
                    color: const Color(0xFF20C997),
                  ),
                ),
              ],
            )
                .animate()
                .fadeIn(delay: 200.ms, duration: 400.ms)
                .slideY(begin: 0.05),

            const Gap(28),

            // ─── Menu Options ───
            CustomCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuTile(
                    icon: Icons.person_outline,
                    label: 'Edit Profile',
                    onTap: () => _showEditProfileDialog(context, auth),
                  ),
                  _divider(theme),
                  _MenuTile(
                    icon: Icons.lock_outline,
                    label: 'Change Password',
                    onTap: () => _showChangePasswordDialog(context, auth),
                  ),
                  _divider(theme),
                  _MenuTile(
                    icon: Icons.fingerprint,
                    label: 'Biometric Settings',
                    subtitle: auth.isBiometricEnabled ? 'Enabled' : 'Disabled',
                    onTap: () => Navigator.pushNamed(context, '/settings'),
                  ),
                  _divider(theme),
                  _MenuTile(
                    icon: Icons.notifications_outlined,
                    label: 'Notification Settings',
                    onTap: () => Navigator.pushNamed(context, '/settings'),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

            const Gap(16),

            CustomCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuTile(
                    icon: Icons.help_outline,
                    label: 'Help & Support',
                    onTap: () => Navigator.pushNamed(context, '/help-support'),
                  ),
                  _divider(theme),
                  _MenuTile(
                    icon: Icons.info_outline,
                    label: 'About',
                    subtitle: 'Version 1.0.0',
                    onTap: () => Navigator.pushNamed(context, '/about'),
                  ),
                  _divider(theme),
                  _MenuTile(
                    icon: Icons.privacy_tip_outlined,
                    label: 'Privacy Policy',
                    onTap: () => Navigator.pushNamed(context, '/privacy-policy'),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

            const Gap(24),

            CustomButton(
              text: 'Sign Out',
              leftIcon: Icons.logout,
              variant: ButtonVariant.outline,
              fullWidth: true,
              onPressed: () => _showLogoutDialog(context),
            ).animate().fadeIn(delay: 500.ms, duration: 400.ms),

            const Gap(20),
          ],
        ),
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

  String _calcStorage(DocumentProvider docs) {
    final totalBytes = docs.documents.fold<int>(0, (sum, d) => sum + d.fileSize);
    if (totalBytes < 1024 * 1024) {
      return '${(totalBytes / 1024).toStringAsFixed(0)} KB';
    }
    return '${(totalBytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Sign Out'),
        content: const Text('Are you sure you want to sign out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              await context.read<AuthProvider>().logout();
              if (context.mounted) {
                Navigator.pop(ctx);
                Navigator.pushNamedAndRemoveUntil(
                    context, '/login', (_) => false);
              }
            },
            child: const Text(
              'Sign Out',
              style: TextStyle(color: Color(0xFFFA5252)),
            ),
          ),
        ],
      ),
    );
  }

  void _showEditProfileDialog(BuildContext context, AuthProvider auth) {
    final nameController = TextEditingController(text: auth.user?.name ?? '');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Edit Profile'),
        content: TextField(
          controller: nameController,
          decoration: InputDecoration(
            labelText: 'Full Name',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              final name = nameController.text.trim();
              if (name.isEmpty) return;
              final success = await auth.updateProfile(name);
              if (ctx.mounted) {
                Navigator.pop(ctx);
                if (success) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: const Text('Profile updated successfully'),
                      backgroundColor: const Color(0xFF20C997),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  );
                }
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showChangePasswordDialog(BuildContext context, AuthProvider auth) {
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
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDark
            ? Colors.white.withOpacity(0.04)
            : Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isDark
              ? Colors.white.withOpacity(0.06)
              : Colors.grey.withOpacity(0.1),
        ),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 22),
          const Gap(8),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.w800,
            ),
          ),
          const Gap(2),
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.5),
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }
}

class _MenuTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? subtitle;
  final VoidCallback onTap;

  const _MenuTile({
    required this.icon,
    required this.label,
    this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ListTile(
      onTap: onTap,
      leading: Icon(
        icon,
        color: theme.colorScheme.onSurface.withOpacity(0.6),
        size: 22,
      ),
      title: Text(
        label,
        style: theme.textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle!,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.4),
              ),
            )
          : null,
      trailing: Icon(
        Icons.chevron_right,
        color: theme.colorScheme.onSurface.withOpacity(0.3),
        size: 20,
      ),
    );
  }
}
