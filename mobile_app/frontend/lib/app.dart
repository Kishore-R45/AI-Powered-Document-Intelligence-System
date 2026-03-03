import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'config/routes.dart';
import 'api/api_config.dart';
import 'providers/theme_provider.dart';
import 'providers/auth_provider.dart';

class DocIntelApp extends StatefulWidget {
  const DocIntelApp({super.key});

  @override
  State<DocIntelApp> createState() => _DocIntelAppState();
}

class _DocIntelAppState extends State<DocIntelApp>
    with WidgetsBindingObserver {
  final GlobalKey<NavigatorState> _navigatorKey = GlobalKey<NavigatorState>();

  /// Tracks when the app truly entered the `paused` (background) state.
  /// Null when the app is in the foreground.
  DateTime? _pausedAt;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final auth = context.read<AuthProvider>();

    if (state == AppLifecycleState.paused) {
      // App truly going to background (not just notification shade)
      _pausedAt = DateTime.now();
      auth.updateActivity();
    } else if (state == AppLifecycleState.resumed) {
      // Only check auto-lock if we were truly paused (backgrounded),
      // AND we stayed in the background long enough.
      // Pulling down the notification shade triggers inactive → resumed
      // (NOT paused), so _pausedAt stays null → no lock.
      if (_pausedAt != null) {
        final pauseDuration = DateTime.now().difference(_pausedAt!);
        _pausedAt = null; // reset

        if (pauseDuration.inMinutes >= ApiConfig.autoLockMinutes) {
          auth.checkAutoLock().then((_) {
            if (auth.isLocked) {
              _navigatorKey.currentState?.pushNamedAndRemoveUntil(
                '/login',
                (route) => false,
              );
            }
          });
        }
      }
      // Always refresh last-active on resume so future checks are fresh
      auth.updateActivity();
    }
    // AppLifecycleState.inactive (notification shade, phone call, etc.)
    // → intentionally ignored — no lock, no timestamp update.
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();

    return MaterialApp(
      title: 'InfoVault',
      debugShowCheckedModeBanner: false,
      navigatorKey: _navigatorKey,

      // Theme
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeProvider.themeMode,

      // Routing
      initialRoute: AppRoutes.splash,
      onGenerateRoute: AppRoutes.generateRoute,

      // ScrollBehavior for smooth scrolling
      scrollBehavior: const MaterialScrollBehavior().copyWith(
        physics: const BouncingScrollPhysics(),
      ),
    );
  }
}
