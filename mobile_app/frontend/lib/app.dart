import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'config/routes.dart';
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
      // App going to background → save last-active time
      auth.updateActivity();
    } else if (state == AppLifecycleState.resumed) {
      // App returning from background → check if auto-lock needed
      auth.checkAutoLock().then((_) {
        if (auth.isLocked) {
          _navigatorKey.currentState?.pushNamedAndRemoveUntil(
            '/lock',
            (route) => false,
          );
        }
      });
    }
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
