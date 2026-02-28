class AppConstants {
  AppConstants._();

  // ─── App Info ───
  static const String appName = 'InfoVault';
  static const String appTagline = 'Your Documents, Organized & Queryable';
  static const String appVersion = '1.0.0';
  static const String appDescription =
      'Securely upload personal documents and retrieve verified information '
      'instantly through intelligent queries.';

  // ─── Auto-lock ───
  static const int autoLockDurationMinutes = 5;

  // ─── Document Categories ───
  static const List<String> documentCategories = [
    'All',
    'Identity',
    'Education',
    'Finance',
    'Insurance',
    'Medical',
    'Legal',
    'Other',
  ];

  // ─── Document Types ───
  static const List<String> documentTypes = [
    'PAN Card',
    'Aadhaar Card',
    'Passport',
    'Driving License',
    'Voter ID',
    'Degree Certificate',
    'Marksheet',
    'Income Tax Return',
    'Salary Slip',
    'Insurance Policy',
    'Medical Report',
    'Birth Certificate',
    'Other',
  ];

  // ─── Animation Durations ───
  static const Duration animFast = Duration(milliseconds: 200);
  static const Duration animNormal = Duration(milliseconds: 300);
  static const Duration animSlow = Duration(milliseconds: 500);
  static const Duration animVerySlow = Duration(milliseconds: 800);

  // ─── Spacing ───
  static const double spacingXs = 4.0;
  static const double spacingSm = 8.0;
  static const double spacingMd = 16.0;
  static const double spacingLg = 24.0;
  static const double spacingXl = 32.0;
  static const double spacing2xl = 48.0;

  // ─── Suggested Chat Questions ───
  static const List<String> suggestedQuestions = [
    'What is my PAN number?',
    'When does my passport expire?',
    'What is my CGPA?',
    'Show my insurance policy details',
    'What is my Aadhaar number?',
    'List all my expiring documents',
  ];
}
