import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateAfterInit();
  }

  Future<void> _navigateAfterInit() async {
    // Wait minimum splash time + for auth to initialize
    await Future.delayed(const Duration(seconds: 2));

    if (!mounted) return;

    final auth = context.read<AuthProvider>();

    // Wait for auth provider to finish initialization
    while (!auth.initialized) {
      await Future.delayed(const Duration(milliseconds: 100));
      if (!mounted) return;
    }

    if (!mounted) return;

    if (auth.isAuthenticated) {
      if (auth.isLocked) {
        Navigator.pushReplacementNamed(context, '/lock');
      } else {
        Navigator.pushReplacementNamed(context, '/home');
      }
    } else if (auth.hasCompletedFirstLogin && auth.isBiometricEnabled) {
      // Has biometric token but session expired → show lock screen
      Navigator.pushReplacementNamed(context, '/lock');
    } else {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isDark
                ? [const Color(0xFF0F1120), const Color(0xFF1A1C2A)]
                : [AppTheme.brand600, AppTheme.brand800],
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Spacer(flex: 3),

            // ─── Logo ───
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                borderRadius: BorderRadius.circular(28),
                border: Border.all(
                  color: Colors.white.withOpacity(0.2),
                  width: 1.5,
                ),
              ),
              child: const Icon(
                Icons.shield_outlined,
                color: Colors.white,
                size: 52,
              ),
            )
                .animate()
                .fadeIn(duration: 600.ms)
                .scale(
                  begin: const Offset(0.5, 0.5),
                  end: const Offset(1.0, 1.0),
                  duration: 600.ms,
                  curve: Curves.easeOutBack,
                ),

            const SizedBox(height: 28),

            // ─── App Name ───
            const Text(
              'InfoVault',
              style: TextStyle(
                color: Colors.white,
                fontSize: 32,
                fontWeight: FontWeight.w800,
                letterSpacing: -0.5,
              ),
            ).animate().fadeIn(delay: 300.ms, duration: 500.ms),

            const SizedBox(height: 8),

            Text(
              'Your Documents, Organized & Queryable',
              style: TextStyle(
                color: Colors.white.withOpacity(0.7),
                fontSize: 14,
                fontWeight: FontWeight.w400,
              ),
            ).animate().fadeIn(delay: 500.ms, duration: 500.ms),

            const Spacer(flex: 2),

            // ─── Loading Indicator ───
            SizedBox(
              width: 36,
              height: 36,
              child: CircularProgressIndicator(
                strokeWidth: 2.5,
                color: Colors.white.withOpacity(0.6),
              ),
            ).animate().fadeIn(delay: 800.ms, duration: 400.ms),

            const SizedBox(height: 16),

            Text(
              'Securing your documents...',
              style: TextStyle(
                color: Colors.white.withOpacity(0.5),
                fontSize: 13,
              ),
            ).animate().fadeIn(delay: 1000.ms, duration: 400.ms),

            const Spacer(flex: 1),

            // ─── Footer ───
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.lock_outline,
                  size: 14,
                  color: Colors.white.withOpacity(0.4),
                ),
                const SizedBox(width: 6),
                Text(
                  'Enterprise-grade Security',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.4),
                    fontSize: 12,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
