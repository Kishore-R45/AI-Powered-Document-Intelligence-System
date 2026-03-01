/// API configuration for connecting to the InfoVault Mobile backend.
/// Change [baseUrl] to your deployed HuggingFace Spaces URL.
class ApiConfig {
  ApiConfig._();

  /// Base URL of the mobile backend API.
  /// For HuggingFace Spaces: https://<your-mobile-space>.hf.space
  /// For local development: http://10.0.2.2:7860 (Android emulator)
  ///                         http://localhost:7860 (Web/Desktop)
  ///                         http://<your-pc-ip>:7860 (physical device)
  static const String baseUrl = 'http://192.168.1.16:5001';

  /// API prefix — all endpoints sit under /api
  static const String apiPrefix = '/api';

  /// Full API base
  static String get apiBase => '$baseUrl$apiPrefix';

  /// Request timeout in seconds
  static const int connectTimeout = 30;
  static const int receiveTimeout = 120;
  static const int uploadTimeout = 300;

  /// Auto-lock duration in minutes
  static const int autoLockMinutes = 5;
}
