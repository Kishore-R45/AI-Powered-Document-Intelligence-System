import 'package:flutter/material.dart';
import '../models/document_model.dart';
import '../models/extracted_data_model.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/lock/lock_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/signup_screen.dart';
import '../screens/auth/forgot_password_screen.dart';
import '../screens/auth/otp_verification_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/documents/document_viewer_screen.dart';
import '../screens/documents/scan_document_screen.dart';
import '../screens/upload/upload_screen.dart';
import '../screens/extracted_data/extracted_data_screen.dart';
import '../screens/extracted_data/document_data_detail_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/settings/settings_screen.dart';
import '../screens/help/help_support_screen.dart';
import '../screens/about/about_screen.dart';
import '../screens/privacy/privacy_policy_screen.dart';

class AppRoutes {
  static const String splash = '/';
  static const String lock = '/lock';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String otpVerification = '/otp-verification';
  static const String home = '/home';
  static const String documentViewer = '/document-viewer';
  static const String scan = '/scan';
  static const String upload = '/upload';
  static const String extractedData = '/extracted-data';
  static const String documentData = '/document-data';
  static const String profile = '/profile';
  static const String settings = '/settings';
  static const String helpSupport = '/help-support';
  static const String about = '/about';
  static const String privacyPolicy = '/privacy-policy';

  static Route<dynamic> generateRoute(RouteSettings routeSettings) {
    switch (routeSettings.name) {
      case splash:
        return _buildRoute(const SplashScreen(), routeSettings);

      case lock:
        return _buildRoute(const LockScreen(), routeSettings);

      case login:
        return _buildRoute(const LoginScreen(), routeSettings);

      case signup:
        return _buildRoute(const SignupScreen(), routeSettings);

      case forgotPassword:
        return _buildRoute(const ForgotPasswordScreen(), routeSettings);

      case otpVerification:
        return _buildRoute(
          const OTPVerificationScreen(),
          routeSettings,
        );

      case home:
        return _buildRoute(const HomeScreen(), routeSettings);

      case documentViewer:
        final doc = routeSettings.arguments as DocumentModel;
        return _buildRoute(
          DocumentViewerScreen(document: doc),
          routeSettings,
        );

      case scan:
        return _buildRoute(const ScanDocumentScreen(), routeSettings);

      case upload:
        return _buildRoute(const UploadScreen(), routeSettings);

      case extractedData:
        return _buildRoute(const ExtractedDataScreen(), routeSettings);

      case documentData:
        final data = routeSettings.arguments as ExtractedDataModel;
        return _buildRoute(
          DocumentDataDetailScreen(extractedData: data),
          routeSettings,
        );

      case profile:
        return _buildRoute(const ProfileScreen(), routeSettings);

      case settings:
        return _buildRoute(const SettingsScreen(), routeSettings);

      case helpSupport:
        return _buildRoute(const HelpSupportScreen(), routeSettings);

      case about:
        return _buildRoute(const AboutScreen(), routeSettings);

      case privacyPolicy:
        return _buildRoute(const PrivacyPolicyScreen(), routeSettings);

      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(
              child: Text('No route defined for ${routeSettings.name}'),
            ),
          ),
        );
    }
  }

  static PageRouteBuilder _buildRoute(Widget page, RouteSettings settings) {
    return PageRouteBuilder(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(1.0, 0.0);
        const end = Offset.zero;
        const curve = Curves.easeInOutCubic;

        final tween = Tween(begin: begin, end: end).chain(
          CurveTween(curve: curve),
        );
        final offsetAnimation = animation.drive(tween);

        final fadeTween = Tween(begin: 0.0, end: 1.0).chain(
          CurveTween(curve: curve),
        );
        final fadeAnimation = animation.drive(fadeTween);

        return SlideTransition(
          position: offsetAnimation,
          child: FadeTransition(
            opacity: fadeAnimation,
            child: child,
          ),
        );
      },
      transitionDuration: const Duration(milliseconds: 350),
      reverseTransitionDuration: const Duration(milliseconds: 300),
    );
  }
}
