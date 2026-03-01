import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/document_model.dart';
import '../models/extracted_data_model.dart';

/// Manages Hive boxes & SharedPreferences for offline data caching.
class LocalStorageService {
  static const String _documentsBoxName = 'documents';
  static const String _extractedDataBoxName = 'extracted_data';
  static const String _settingsBoxName = 'settings';

  // SharedPreferences keys
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyBiometricToken = 'biometric_token';
  static const String _keyDeviceId = 'device_id';
  static const String _keyBiometricEnabled = 'biometric_enabled';
  static const String _keyAutoLockEnabled = 'auto_lock_enabled';
  static const String _keyLastActiveTime = 'last_active_time';
  static const String _keyUserJson = 'user_json';
  static const String _keyPasswordHash = 'password_hash';
  static const String _keyLastEmail = 'last_email';
  static const String _keyUserId = 'user_id';
  static const String _keyPushNotifications = 'push_notifications';
  static const String _keyExpiryReminders = 'expiry_reminders';
  static const String _docFilesBoxName = 'doc_files';

  static SharedPreferences? _prefs;
  static bool _hivInitialized = false;

  LocalStorageService._();

  // ─── Initialization ───

  static Future<void> initialize() async {
    if (!_hivInitialized) {
      await Hive.initFlutter();
      await Hive.openBox<String>(_documentsBoxName);
      await Hive.openBox<String>(_extractedDataBoxName);
      await Hive.openBox<String>(_settingsBoxName);
      await Hive.openBox<String>(_docFilesBoxName);
      _hivInitialized = true;
    }
    _prefs ??= await SharedPreferences.getInstance();
  }

  static SharedPreferences get prefs {
    if (_prefs == null) throw Exception('LocalStorageService not initialized');
    return _prefs!;
  }

  // ─── Token Management ───

  static String? get accessToken => prefs.getString(_keyAccessToken);
  static String? get refreshToken => prefs.getString(_keyRefreshToken);
  static String? get biometricToken => prefs.getString(_keyBiometricToken);
  static String? get deviceId => prefs.getString(_keyDeviceId);

  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await prefs.setString(_keyAccessToken, accessToken);
    await prefs.setString(_keyRefreshToken, refreshToken);
  }

  static Future<void> saveBiometricToken(String token) async {
    await prefs.setString(_keyBiometricToken, token);
  }

  static Future<void> saveDeviceId(String id) async {
    await prefs.setString(_keyDeviceId, id);
  }

  static Future<void> clearTokens() async {
    await prefs.remove(_keyAccessToken);
    await prefs.remove(_keyRefreshToken);
    await prefs.remove(_keyBiometricToken);
  }

  // ─── Biometric / Auto-lock Preferences ───

  static bool get biometricEnabled =>
      prefs.getBool(_keyBiometricEnabled) ?? false;

  static Future<void> setBiometricEnabled(bool enabled) async {
    await prefs.setBool(_keyBiometricEnabled, enabled);
  }

  static bool get autoLockEnabled =>
      prefs.getBool(_keyAutoLockEnabled) ?? true;

  static Future<void> setAutoLockEnabled(bool enabled) async {
    await prefs.setBool(_keyAutoLockEnabled, enabled);
  }

  static bool get pushNotificationsEnabled =>
      prefs.getBool(_keyPushNotifications) ?? true;

  static Future<void> setPushNotificationsEnabled(bool enabled) async {
    await prefs.setBool(_keyPushNotifications, enabled);
  }

  static bool get expiryRemindersEnabled =>
      prefs.getBool(_keyExpiryReminders) ?? true;

  static Future<void> setExpiryRemindersEnabled(bool enabled) async {
    await prefs.setBool(_keyExpiryReminders, enabled);
  }

  static DateTime? get lastActiveTime {
    final ms = prefs.getInt(_keyLastActiveTime);
    return ms != null ? DateTime.fromMillisecondsSinceEpoch(ms) : null;
  }

  static Future<void> updateLastActiveTime() async {
    await prefs.setInt(
        _keyLastActiveTime, DateTime.now().millisecondsSinceEpoch);
  }

  // ─── Offline Auth Cache ───

  /// Save a SHA-256 hash of email+password for offline login.
  static Future<void> savePasswordHash(String email, String password) async {
    final hash = sha256.convert(utf8.encode('$email:$password')).toString();
    await prefs.setString(_keyPasswordHash, hash);
    await prefs.setString(_keyLastEmail, email.toLowerCase());
  }

  /// Verify credentials offline against the cached hash.
  static bool verifyPasswordOffline(String email, String password) {
    final stored = prefs.getString(_keyPasswordHash);
    if (stored == null) return false;
    final hash = sha256.convert(utf8.encode('$email:$password')).toString();
    return hash == stored;
  }

  static String? get lastEmail => prefs.getString(_keyLastEmail);

  /// Whether we have cached credentials for offline login.
  static bool get hasOfflineCredentials =>
      prefs.getString(_keyPasswordHash) != null &&
      prefs.getString(_keyUserJson) != null;

  // ─── User Cache ───

  static String? get userId => prefs.getString(_keyUserId);

  static Future<void> saveUserId(String id) async {
    await prefs.setString(_keyUserId, id);
  }

  static Future<void> saveUserJson(Map<String, dynamic> json) async {
    await prefs.setString(_keyUserJson, jsonEncode(json));
  }

  static Map<String, dynamic>? get cachedUserJson {
    final raw = prefs.getString(_keyUserJson);
    if (raw == null) return null;
    try {
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // ─── Documents Offline Cache (Hive) ───

  static Box<String> get _docsBox => Hive.box<String>(_documentsBoxName);
  static Box<String> get _extractBox =>
      Hive.box<String>(_extractedDataBoxName);

  /// Cache the full documents list as a JSON array string.
  static Future<void> cacheDocuments(List<DocumentModel> docs) async {
    final jsonList = docs.map((d) => d.toJson()).toList();
    await _docsBox.put('all', jsonEncode(jsonList));
  }

  /// Retrieve the cached documents list.
  static List<DocumentModel> getCachedDocuments() {
    final raw = _docsBox.get('all');
    if (raw == null) return [];
    try {
      final list = jsonDecode(raw) as List;
      return list
          .map((j) => DocumentModel.fromJson(j as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  /// Cache extracted data for a single document.
  static Future<void> cacheExtractedData(
      String documentId, ExtractedDataModel data) async {
    await _extractBox.put(documentId, jsonEncode(data.toJson()));
  }

  /// Retrieve cached extracted data for a document.
  static ExtractedDataModel? getCachedExtractedData(String documentId) {
    final raw = _extractBox.get(documentId);
    if (raw == null) return null;
    try {
      return ExtractedDataModel.fromJson(
          jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  /// Cache all extracted data items.
  static Future<void> cacheAllExtractedData(
      List<ExtractedDataModel> items) async {
    for (final item in items) {
      await _extractBox.put(item.documentId, jsonEncode(item.toJson()));
    }
  }

  /// Get all cached extracted data.
  static List<ExtractedDataModel> getAllCachedExtractedData() {
    final results = <ExtractedDataModel>[];
    for (final key in _extractBox.keys) {
      final raw = _extractBox.get(key);
      if (raw != null) {
        try {
          results.add(ExtractedDataModel.fromJson(
              jsonDecode(raw) as Map<String, dynamic>));
        } catch (_) {}
      }
    }
    return results;
  }

  // ─── Document File Paths (for local viewing) ───

  static Box<String> get _docFilesBox => Hive.box<String>(_docFilesBoxName);

  /// Save local file path for a document.
  static Future<void> saveDocFilePath(String documentId, String filePath) async {
    await _docFilesBox.put(documentId, filePath);
  }

  /// Get local file path for a document.
  static String? getDocFilePath(String documentId) {
    return _docFilesBox.get(documentId);
  }

  /// Remove a document's local file path.
  static Future<void> removeDocFilePath(String documentId) async {
    await _docFilesBox.delete(documentId);
  }

  // ─── Clear All ───

  static Future<void> clearAll() async {
    await clearTokens();
    await prefs.remove(_keyUserJson);
    await prefs.remove(_keyBiometricEnabled);
    await prefs.remove(_keyAutoLockEnabled);
    await prefs.remove(_keyLastActiveTime);
    await prefs.remove(_keyPasswordHash);
    await prefs.remove(_keyLastEmail);
    await _docsBox.clear();
    await _extractBox.clear();
    await _docFilesBox.clear();
  }
}
