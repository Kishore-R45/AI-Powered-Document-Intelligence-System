import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:gap/gap.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../config/theme.dart';
import '../../widgets/common/custom_card.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  static const String _portfolioUrl = 'https://kishore-portfolio-45.netlify.app';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('About'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // ─── App Logo & Info ───
          Center(
            child: Column(
              children: [
                Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppTheme.brand600, AppTheme.brand400],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.brand600.withOpacity(0.3),
                        blurRadius: 20,
                        offset: const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.description_outlined,
                    color: Colors.white,
                    size: 44,
                  ),
                )
                    .animate()
                    .fadeIn(duration: 500.ms)
                    .scale(begin: const Offset(0.8, 0.8)),
                const Gap(20),
                Text(
                  'InfoVault',
                  style: theme.textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ).animate().fadeIn(delay: 100.ms),
                const Gap(4),
                Text(
                  'AI-Powered Document Intelligence',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  ),
                ).animate().fadeIn(delay: 150.ms),
                const Gap(6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.brand600.withOpacity(isDark ? 0.15 : 0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'Version 1.0.0',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: AppTheme.brand600,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ).animate().fadeIn(delay: 200.ms),
              ],
            ),
          ),

          const Gap(32),

          // ─── App Features ───
          Text(
            'APP FEATURES',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              fontSize: 11,
            ),
          ).animate().fadeIn(delay: 250.ms, duration: 300.ms),
          const Gap(12),

          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _FeatureTile(
                  icon: Icons.cloud_upload_outlined,
                  iconColor: AppTheme.brand600,
                  title: 'Smart Document Upload',
                  subtitle: 'Upload PDFs, images, or scan documents with your camera',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.auto_awesome,
                  iconColor: const Color(0xFF7C4DFF),
                  title: 'AI Text Extraction',
                  subtitle: 'Automatically extract text and key data from documents',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.smart_toy_outlined,
                  iconColor: const Color(0xFF339AF0),
                  title: 'AI-Powered Q&A',
                  subtitle: 'Ask questions and get answers from your documents',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.category_outlined,
                  iconColor: const Color(0xFFF59F00),
                  title: 'Smart Categorization',
                  subtitle: 'Auto-categorize documents into organized categories',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.notifications_active_outlined,
                  iconColor: const Color(0xFFFA5252),
                  title: 'Expiry Reminders',
                  subtitle: 'Get notified before your important documents expire',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.fingerprint,
                  iconColor: const Color(0xFF20C997),
                  title: 'Biometric Security',
                  subtitle: 'Secure your documents with fingerprint or face ID',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.cloud_off_outlined,
                  iconColor: const Color(0xFF868E96),
                  title: 'Offline Access',
                  subtitle: 'View your documents even without internet connection',
                ),
                _featureDivider(theme),
                _FeatureTile(
                  icon: Icons.share_outlined,
                  iconColor: const Color(0xFF339AF0),
                  title: 'Easy Sharing',
                  subtitle: 'Share documents and extracted data with anyone',
                ),
              ],
            ),
          ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

          const Gap(28),

          // ─── Developer Section ───
          Text(
            'DEVELOPER',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              fontSize: 11,
            ),
          ).animate().fadeIn(delay: 400.ms, duration: 300.ms),
          const Gap(12),

          CustomCard(
            child: Column(
              children: [
                Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        const Color(0xFF7C4DFF),
                        const Color(0xFF448AFF),
                      ],
                    ),
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF7C4DFF).withOpacity(0.3),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Text(
                      'KR',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
                const Gap(16),
                Text(
                  'Developed by',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                  ),
                ),
                const Gap(4),
                Text(
                  'Kishore R',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Gap(16),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _launchPortfolio(context),
                    icon: const Icon(Icons.language, size: 20),
                    label: const Text('Visit Portfolio'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: AppTheme.brand600,
                      side: BorderSide(
                        color: AppTheme.brand600.withOpacity(0.3),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const Gap(8),
                Text(
                  _portfolioUrl,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 450.ms, duration: 400.ms),

          const Gap(28),

          // ─── Tech Stack ───
          Text(
            'BUILT WITH',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              fontSize: 11,
            ),
          ).animate().fadeIn(delay: 500.ms, duration: 300.ms),
          const Gap(12),

          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _TechChip(label: 'Flutter', color: const Color(0xFF027DFD)),
              _TechChip(label: 'Flask', color: const Color(0xFF000000)),
              _TechChip(label: 'MongoDB', color: const Color(0xFF47A248)),
              _TechChip(label: 'Pinecone', color: const Color(0xFF000000)),
              _TechChip(label: 'HuggingFace AI', color: const Color(0xFFFF9D00)),
              _TechChip(label: 'Material 3', color: AppTheme.brand600),
            ],
          ).animate().fadeIn(delay: 550.ms, duration: 400.ms),

          const Gap(32),

          Center(
            child: Text(
              '© 2025 InfoVault. All rights reserved.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withOpacity(0.3),
              ),
            ),
          ).animate().fadeIn(delay: 600.ms, duration: 400.ms),
          const Gap(20),
        ],
      ),
    );
  }

  Widget _featureDivider(ThemeData theme) {
    return Divider(
      height: 1,
      indent: 56,
      color: theme.colorScheme.onSurface.withOpacity(0.06),
    );
  }

  Future<void> _launchPortfolio(BuildContext context) async {
    final uri = Uri.parse(_portfolioUrl);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('Could not open portfolio link'),
            backgroundColor: const Color(0xFFFA5252),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        );
      }
    }
  }
}

class _FeatureTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;

  const _FeatureTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return ListTile(
      leading: Container(
        width: 38,
        height: 38,
        decoration: BoxDecoration(
          color: isDark ? iconColor.withOpacity(0.12) : iconColor.withOpacity(0.08),
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
      subtitle: Text(
        subtitle,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurface.withOpacity(0.4),
          fontSize: 12,
        ),
      ),
    );
  }
}

class _TechChip extends StatelessWidget {
  final String label;
  final Color color;

  const _TechChip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: isDark ? color.withOpacity(0.1) : color.withOpacity(0.06),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: color.withOpacity(0.15),
        ),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: isDark ? color.withOpacity(0.8) : color,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
