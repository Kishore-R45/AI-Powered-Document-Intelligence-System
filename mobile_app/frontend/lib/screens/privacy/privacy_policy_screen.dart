import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:gap/gap.dart';
import '../../config/theme.dart';
import '../../widgets/common/custom_card.dart';

class PrivacyPolicyScreen extends StatelessWidget {
  const PrivacyPolicyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Privacy Policy'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // ─── Header ───
          Center(
            child: Column(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    color: AppTheme.brand600.withOpacity(isDark ? 0.15 : 0.1),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Icon(
                    Icons.privacy_tip_outlined,
                    color: AppTheme.brand600,
                    size: 30,
                  ),
                ),
                const Gap(16),
                Text(
                  'Privacy Policy',
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const Gap(6),
                Text(
                  'Last updated: March 2026',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.4),
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(duration: 400.ms),

          const Gap(28),

          _PolicySection(
            title: '1. Information We Collect',
            content:
                'When you use InfoVault, we collect the following information:\n\n'
                '• Account Information: Your name, email address, and encrypted password when you create an account.\n\n'
                '• Documents: Files you upload including PDFs, images, and scanned documents for processing and storage.\n\n'
                '• Usage Data: How you interact with the app, including features used, documents accessed, and AI queries made.\n\n'
                '• Device Information: Device type, operating system, and app version for providing a better experience.',
          ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

          _PolicySection(
            title: '2. How We Use Your Information',
            content:
                'We use your information to:\n\n'
                '• Provide and maintain the InfoVault service, including document storage, AI-powered text extraction, and Q&A features.\n\n'
                '• Process and analyze your documents using AI services to extract text, key-value data, and enable intelligent search.\n\n'
                '• Send notifications about document expiry reminders and important updates when you enable this feature.\n\n'
                '• Improve our services through aggregated, anonymized usage analytics.\n\n'
                '• Secure your account with JWT authentication, biometric login, and auto-lock features.',
          ).animate().fadeIn(delay: 150.ms, duration: 400.ms),

          _PolicySection(
            title: '3. Data Storage & Security',
            content:
                'Your data security is our top priority:\n\n'
                '• Documents are stored securely in your mobile.\n\n'
                '• Passwords are hashed using industry-standard algorithms and are never stored in plain text.\n\n'
                '• Authentication is handled through JWT tokens with automatic expiration.\n\n'
                '• Biometric data (fingerprint/face ID) is processed locally on your device and never sent to our servers.\n\n'
                '• Auto-lock protects your data when the app is inactive for an extended period.\n\n'
                '• All API communications are encrypted using HTTPS/TLS.',
          ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

          _PolicySection(
            title: '4. AI & Document Processing',
            content:
                '• Uploaded documents are processed using AI models to extract text and key information.\n\n'
                '• Document embeddings are generated and stored in a vector database (Pinecone) to power the Q&A feature.\n\n'
                '• AI queries are processed using HuggingFace Inference API to generate accurate, context-aware responses.\n\n'
                '• Your documents are only used to serve you and are never shared with other users.',
          ).animate().fadeIn(delay: 250.ms, duration: 400.ms),

          _PolicySection(
            title: '5. Offline Data',
            content:
                '• InfoVault caches certain data locally on your device for offline access, including viewed documents and login credentials.\n\n'
                '• Local data is encrypted using secure storage mechanisms.\n\n'
                '• You can clear cached data at any time through Settings → Clear Cache.',
          ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

          _PolicySection(
            title: '6. Third-Party Services',
            content:
                'InfoVault uses the following third-party services:\n\n'
                '• MongoDB Atlas — For secure database hosting.\n\n'
                '• Amazon S3 — For encrypted document file storage.\n\n'
                '• Pinecone — For vector database storage enabling AI search.\n\n'
                '• HuggingFace — For AI model inference and text processing.\n\n'
                'Each service has its own privacy policy governing the data they process.',
          ).animate().fadeIn(delay: 350.ms, duration: 400.ms),

          _PolicySection(
            title: '7. Notifications',
            content:
                '• Push notifications and expiry reminders are optional features that can be enabled or disabled in Settings.\n\n'
                '• We will only send notifications you have explicitly opted into.\n\n'
                '• You can manage your notification preferences at any time.',
          ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

          _PolicySection(
            title: '8. Your Rights',
            content:
                'You have the right to:\n\n'
                '• Access your personal data and uploaded documents at any time.\n\n'
                '• Update your profile information through the Edit Profile feature.\n\n'
                '• Delete your documents individually or request account deletion.\n\n'
                '• Export your data in standard formats.\n\n'
                '• Opt out of notifications and optional data collection features.',
          ).animate().fadeIn(delay: 450.ms, duration: 400.ms),

          _PolicySection(
            title: '9. Data Retention',
            content:
                '• Your documents and account data are retained as long as your account is active.\n\n'
                '• If you delete a document, it is permanently removed from our storage.\n\n'
                '• Chat history can be cleared at any time through the chat interface.\n\n'
                '• Upon account deletion, all associated data will be permanently removed within 30 days.',
          ).animate().fadeIn(delay: 500.ms, duration: 400.ms),

          _PolicySection(
            title: '10. Contact Us',
            content:
                'If you have questions or concerns about this Privacy Policy or our data practices, please contact us:\n\n'
                '📧 Email: infovault.notification@gmail.com\n\n'
                'We will respond to your inquiry within 48 hours.',
          ).animate().fadeIn(delay: 550.ms, duration: 400.ms),

          const Gap(24),

          Center(
            child: Text(
              '© 2026 InfoVault. All rights reserved.',
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
}

class _PolicySection extends StatelessWidget {
  final String title;
  final String content;

  const _PolicySection({required this.title, required this.content});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const Gap(10),
          Text(
            content,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.6),
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }
}
