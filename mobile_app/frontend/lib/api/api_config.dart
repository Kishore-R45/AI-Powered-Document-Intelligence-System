/// API configuration for connecting to the InfoVault backend.
/// Change [baseUrl] to your deployed HuggingFace Spaces URL.
class ApiConfig {
  ApiConfig._();

  /// Base URL of the backend API.
  /// For HuggingFace Spaces: https://<your-space>.hf.space
  /// For local development: http://10.0.2.2:7860 (Android emulator)
  ///                         http://localhost:7860 (Web/Desktop)
  static const String baseUrl = 'https://kishore200630-info-vault.hf.space';

  /// API prefix — all endpoints sit under /api
  static const String apiPrefix = '/api';

  /// Full API base
  static String get apiBase => '$baseUrl$apiPrefix';

  /// Request timeout in seconds
  static const int connectTimeout = 30;
  static const int receiveTimeout = 60;
  static const int uploadTimeout = 120;
}
