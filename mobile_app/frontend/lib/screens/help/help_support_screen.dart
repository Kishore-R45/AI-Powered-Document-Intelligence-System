import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:gap/gap.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../config/theme.dart';
import '../../widgets/common/custom_card.dart';

class HelpSupportScreen extends StatelessWidget {
  const HelpSupportScreen({super.key});

  static const String _supportEmail = 'infovault.notification@gmail.com';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Help & Support'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // ─── Contact Support ───
          CustomCard(
            child: Column(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [AppTheme.brand600, AppTheme.brand400],
                    ),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: const Icon(
                    Icons.support_agent,
                    color: Colors.white,
                    size: 30,
                  ),
                ),
                const Gap(16),
                Text(
                  'Need Help?',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Gap(6),
                Text(
                  'We\'re here to assist you. Reach out to us\nand we\'ll get back to you as soon as possible.',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.5),
                  ),
                  textAlign: TextAlign.center,
                ),
                const Gap(16),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => _launchEmail(context),
                    icon: const Icon(Icons.email_outlined, size: 20),
                    label: const Text('Email Support'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.brand600,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const Gap(8),
                Text(
                  _supportEmail,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: AppTheme.brand600,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(duration: 400.ms),

          const Gap(24),

          // ─── FAQ Section ───
          Text(
            'FREQUENTLY ASKED QUESTIONS',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              fontSize: 11,
            ),
          ).animate().fadeIn(delay: 100.ms, duration: 300.ms),
          const Gap(12),

          _FaqItem(
            question: 'How do I upload a document?',
            answer:
                'Tap the + button on the home screen or go to the Upload section. '
                'You can upload PDFs, images, or scan documents directly using your camera.',
          ).animate().fadeIn(delay: 150.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'What file formats are supported?',
            answer:
                'InfoVault supports PDF, JPEG, PNG, and other common image formats. '
                'Our AI will automatically extract text and key information from your documents.',
          ).animate().fadeIn(delay: 200.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'How does the AI Q&A work?',
            answer:
                'Once you\'ve uploaded documents, go to the Chat section and ask any question. '
                'The AI assistant will search through your documents and provide accurate answers '
                'with source references.',
          ).animate().fadeIn(delay: 250.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'Is my data secure?',
            answer:
                'Yes! Your documents are encrypted and stored securely. We use JWT-based '
                'authentication, biometric login, and auto-lock features to protect your data. '
                'You can also enable offline access for added convenience.',
          ).animate().fadeIn(delay: 300.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'How do I enable biometric login?',
            answer:
                'Go to Profile → Settings → Security and toggle on Biometric Login. '
                'Make sure your device has fingerprint or face recognition set up.',
          ).animate().fadeIn(delay: 350.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'How do notifications work?',
            answer:
                'InfoVault sends you notifications for document expiry reminders and important '
                'updates. You can customize notification preferences in Settings → Notifications.',
          ).animate().fadeIn(delay: 400.ms, duration: 400.ms),
          const Gap(10),

          _FaqItem(
            question: 'Can I use the app offline?',
            answer:
                'Yes! Documents you\'ve viewed are cached for offline access. You can also '
                'sign in using your cached credentials when there\'s no internet connection.',
          ).animate().fadeIn(delay: 450.ms, duration: 400.ms),

          const Gap(24),

          // ─── Troubleshooting ───
          Text(
            'TROUBLESHOOTING',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.4),
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              fontSize: 11,
            ),
          ).animate().fadeIn(delay: 500.ms, duration: 300.ms),
          const Gap(12),

          CustomCard(
            padding: EdgeInsets.zero,
            child: Column(
              children: [
                _TroubleshootTile(
                  icon: Icons.refresh,
                  iconColor: const Color(0xFF339AF0),
                  title: 'App not loading properly?',
                  subtitle: 'Try closing and reopening the app, or check your internet connection.',
                ),
                Divider(
                  height: 1,
                  indent: 56,
                  color: theme.colorScheme.onSurface.withOpacity(0.06),
                ),
                _TroubleshootTile(
                  icon: Icons.fingerprint,
                  iconColor: const Color(0xFF20C997),
                  title: 'Biometric not working?',
                  subtitle: 'Ensure biometric is set up on your device and enabled in Settings.',
                ),
                Divider(
                  height: 1,
                  indent: 56,
                  color: theme.colorScheme.onSurface.withOpacity(0.06),
                ),
                _TroubleshootTile(
                  icon: Icons.cloud_off,
                  iconColor: const Color(0xFFFA5252),
                  title: 'Upload failing?',
                  subtitle: 'Check your internet connection and ensure the file size is under 10 MB.',
                ),
                Divider(
                  height: 1,
                  indent: 56,
                  color: theme.colorScheme.onSurface.withOpacity(0.06),
                ),
                _TroubleshootTile(
                  icon: Icons.smart_toy_outlined,
                  iconColor: const Color(0xFF7C4DFF),
                  title: 'AI not responding?',
                  subtitle: 'The AI needs uploaded documents to work. Make sure you have at least one document.',
                ),
              ],
            ),
          ).animate().fadeIn(delay: 550.ms, duration: 400.ms),

          const Gap(32),

          // ─── App Version ───
          Center(
            child: Text(
              'InfoVault v1.0.0',
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

  Future<void> _launchEmail(BuildContext context) async {
    final uri = Uri(
      scheme: 'mailto',
      path: _supportEmail,
      queryParameters: {
        'subject': 'InfoVault Support Request',
        'body': 'Hi InfoVault Team,\n\nI need help with:\n\n',
      },
    );
    try {
      await launchUrl(uri);
    } catch (_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Email $_supportEmail for support'),
            backgroundColor: AppTheme.brand600,
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

class _FaqItem extends StatefulWidget {
  final String question;
  final String answer;

  const _FaqItem({required this.question, required this.answer});

  @override
  State<_FaqItem> createState() => _FaqItemState();
}

class _FaqItemState extends State<_FaqItem> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return CustomCard(
      padding: EdgeInsets.zero,
      child: InkWell(
        onTap: () => setState(() => _expanded = !_expanded),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppTheme.brand600.withOpacity(isDark ? 0.12 : 0.08),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      Icons.help_outline,
                      size: 18,
                      color: AppTheme.brand600,
                    ),
                  ),
                  const Gap(12),
                  Expanded(
                    child: Text(
                      widget.question,
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                    size: 22,
                  ),
                ],
              ),
              if (_expanded) ...[
                const Gap(12),
                Padding(
                  padding: const EdgeInsets.only(left: 44),
                  child: Text(
                    widget.answer,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withOpacity(0.6),
                      height: 1.5,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _TroubleshootTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;

  const _TroubleshootTile({
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
