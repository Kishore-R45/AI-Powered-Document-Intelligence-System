import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'package:provider/provider.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'app.dart';
import 'providers/theme_provider.dart';
import 'providers/auth_provider.dart';
import 'providers/document_provider.dart';
import 'providers/extracted_data_provider.dart';
import 'providers/notification_provider.dart';
import 'providers/chat_provider.dart';
import 'services/local_storage_service.dart';
import 'services/push_notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize local storage (Hive + SharedPreferences)
  await LocalStorageService.initialize();

  // Initialize Firebase & push notifications
  try {
    await Firebase.initializeApp();
    // Register the background message handler (must be top-level function)
    FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);
    // Initialize foreground push notification handling
    await PushNotificationService.initialize();
  } catch (e) {
    debugPrint('[Firebase] Initialization failed (push notifications disabled): $e');
  }

  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // Set system overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );

  // Initialize theme provider
  final themeProvider = ThemeProvider();
  await themeProvider.init();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: themeProvider),
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => DocumentProvider()),
        ChangeNotifierProvider(create: (_) => ExtractedDataProvider()),
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),
      ],
      child: const DocIntelApp(),
    ),
  );
}
