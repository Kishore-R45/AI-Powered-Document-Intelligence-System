/// ─── API Configuration ───────────────────────────────────────────────────
///
/// HOW TO CONFIGURE THE BACKEND URL:
///
/// 1. LOCAL DEVELOPMENT (default):
///    - Android Emulator:  'http://10.0.2.2:5001'
///    - Physical Device:   'http://<your-pc-ip>:5001'  (e.g. 'http://192.168.1.16:5001')
///    - Web / Desktop:     'http://localhost:5001'
///
/// 2. HUGGINGFACE SPACES DEPLOYMENT:
///    After uploading the backend to HuggingFace Spaces, replace [baseUrl]
///    with your Space URL:
///    - Format:  'https://<your-username>-<space-name>.hf.space'
///    - Example: 'https://kishore-infovault-mobile.hf.space'
///
///    Just change the [baseUrl] below — everything else stays the same.
///
/// ──────────────────────────────────────────────────────────────────────────
class ApiConfig {
  ApiConfig._();

  /// ╔══════════════════════════════════════════════════════════════════╗
  /// ║  CHANGE THIS URL to your deployed backend                      ║
  /// ║  Local:      'http://192.168.1.16:5001'                        ║
  /// ║  HuggingFace: 'https://<your-space>.hf.space'                  ║
  /// ╚══════════════════════════════════════════════════════════════════╝
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
