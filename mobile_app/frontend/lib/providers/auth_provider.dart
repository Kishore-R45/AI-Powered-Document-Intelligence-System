import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../models/user_model.dart';
import '../api/api_client.dart';
import '../api/api_config.dart';
import '../api/endpoints.dart';
import '../services/biometric_service.dart';
import '../services/local_storage_service.dart';

class AuthProvider extends ChangeNotifier {
  UserModel? _user;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  bool _isBiometricEnabled = false;
  bool _isBiometricAvailable = false;
  bool _isLocked = false; // app auto-lock state
  String? _error;
  bool _hasCompletedFirstLogin = false;
  String? _pendingEmail; // email for OTP / reset flows
  String? _resetToken;
  String? _deviceId;
  bool _initialized = false;

  // Getters
  UserModel? get user => _user;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  bool get isBiometricEnabled => _isBiometricEnabled;
  bool get isBiometricAvailable => _isBiometricAvailable;
  bool get isLocked => _isLocked;
  String? get error => _error;
  bool get hasCompletedFirstLogin => _hasCompletedFirstLogin;
  String? get pendingEmail => _pendingEmail;
  String? get deviceId => _deviceId;
  bool get initialized => _initialized;

  AuthProvider() {
    _initializeAuth();
  }

  // ─── Initialization ───

  Future<void> _initializeAuth() async {
    await LocalStorageService.initialize();
    _deviceId = await _getOrCreateDeviceId();
    _isBiometricAvailable = await BiometricService.isAvailable;
    _isBiometricEnabled = LocalStorageService.biometricEnabled;

    // Try to restore session from stored token
    final storedToken = LocalStorageService.accessToken;
    if (storedToken != null && storedToken.isNotEmpty) {
      await ApiClient.setToken(storedToken);

      // Validate the session with backend
      final res = await ApiClient.post(Endpoints.validateSession, body: {
        'deviceId': _deviceId,
      });

      if (res.success) {
        if (res.data?['user'] != null) {
          _user = UserModel.fromJson(
              res.data!['user'] as Map<String, dynamic>);
        }
        _isAuthenticated = true;
        _hasCompletedFirstLogin = true;

        // Check if we should auto-lock
        if (_shouldAutoLock()) {
          _isLocked = true;
        }
      } else if (_isNetworkError(res.message)) {
        // Offline — restore from cached user data
        final cachedUser = LocalStorageService.cachedUserJson;
        if (cachedUser != null) {
          _user = UserModel.fromJson(cachedUser);
          _isAuthenticated = true;
          _hasCompletedFirstLogin = true;
          if (_shouldAutoLock()) {
            _isLocked = true;
          }
        }
      } else {
        // Token invalid, try refresh
        final refreshed = await _tryRefreshToken();
        if (!refreshed) {
          // Try biometric token if available
          final bioToken = LocalStorageService.biometricToken;
          if (bioToken != null && bioToken.isNotEmpty) {
            // User needs to re-authenticate with biometric
            _isAuthenticated = false;
            _hasCompletedFirstLogin = true; // so splash knows to show lock
          } else {
            // Last resort: check for offline credentials
            final cachedUser = LocalStorageService.cachedUserJson;
            if (cachedUser != null && LocalStorageService.hasOfflineCredentials) {
              _isAuthenticated = false;
              _hasCompletedFirstLogin = true;
            } else {
              await _clearSession();
            }
          }
        }
      }
    }

    _initialized = true;
    notifyListeners();
  }

  Future<String> _getOrCreateDeviceId() async {
    final stored = LocalStorageService.deviceId;
    if (stored != null && stored.isNotEmpty) return stored;
    final newId = const Uuid().v4();
    await LocalStorageService.saveDeviceId(newId);
    return newId;
  }

  bool _shouldAutoLock() {
    if (!LocalStorageService.autoLockEnabled) return false;
    final lastActive = LocalStorageService.lastActiveTime;
    if (lastActive == null) return false;
    final diff = DateTime.now().difference(lastActive).inMinutes;
    return diff >= ApiConfig.autoLockMinutes;
  }

  /// Called when app resumes from background to check auto-lock.
  Future<void> checkAutoLock() async {
    if (!_isAuthenticated) return;
    if (_shouldAutoLock()) {
      _isLocked = true;
      notifyListeners();
    }
  }

  /// Called on user activity to update last-active timestamp.
  Future<void> updateActivity() async {
    await LocalStorageService.updateLastActiveTime();
  }

  // ─── Login ───

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.login,
      body: {
        'email': email,
        'password': password,
        'deviceId': _deviceId,
      },
      auth: false,
    );

    if (res.success && res.data?['token'] != null) {
      await _handleLoginResponse(res.data!);
      // Cache credentials for offline login
      await LocalStorageService.savePasswordHash(email, password);
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      // Try offline login if network error
      if (_isNetworkError(res.message)) {
        final offlineResult = await _tryOfflineLogin(email, password);
        if (offlineResult) {
          _isLoading = false;
          notifyListeners();
          return true;
        }
      }
      _error = res.message ?? 'Invalid email or password';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Check if the error message indicates a network issue.
  bool _isNetworkError(String? message) {
    if (message == null) return false;
    return message.contains('No internet') ||
        message.contains('timed out') ||
        message.contains('Something went wrong') ||
        message.contains('SocketException');
  }

  /// Attempt offline login using cached password hash and user data.
  Future<bool> _tryOfflineLogin(String email, String password) async {
    if (!LocalStorageService.hasOfflineCredentials) return false;
    final verified = LocalStorageService.verifyPasswordOffline(email, password);
    if (!verified) return false;

    // Restore user from cache
    final cachedUser = LocalStorageService.cachedUserJson;
    if (cachedUser != null) {
      _user = UserModel.fromJson(cachedUser);
    }
    _isAuthenticated = true;
    _isLocked = false;
    _hasCompletedFirstLogin = true;
    await LocalStorageService.updateLastActiveTime();
    return true;
  }

  Future<void> _handleLoginResponse(Map<String, dynamic> data) async {
    final accessToken = data['token'] as String;
    final refreshToken = data['refreshToken'] as String?;

    await ApiClient.setToken(accessToken);
    await LocalStorageService.saveTokens(
      accessToken: accessToken,
      refreshToken: refreshToken ?? '',
    );

    if (data['user'] != null) {
      _user = UserModel.fromJson(data['user'] as Map<String, dynamic>);
      _isBiometricEnabled = _user!.biometricEnabled;
      await LocalStorageService.setBiometricEnabled(_isBiometricEnabled);
      await LocalStorageService.saveUserJson(data['user'] as Map<String, dynamic>);
      await LocalStorageService.saveUserId(_user!.id);
    }

    _isAuthenticated = true;
    _isLocked = false;
    _hasCompletedFirstLogin = true;
    await LocalStorageService.updateLastActiveTime();
  }

  // ─── Biometric Login ───

  /// Authenticate using device biometric + stored biometric token.
  /// Works offline: if biometric passes locally and we have cached user data, grant access.
  Future<bool> authenticateWithBiometric() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    // Step 1: Local biometric check (fingerprint / face)
    final localAuth = await BiometricService.authenticate(
      reason: 'Authenticate to unlock InfoVault',
    );
    if (!localAuth) {
      _error = 'Biometric authentication failed';
      _isLoading = false;
      notifyListeners();
      return false;
    }

    // Step 2: Try online biometric-token verification
    final storedUserId = _user?.id ?? LocalStorageService.userId;
    if (storedUserId != null && storedUserId.isNotEmpty) {
      final res = await ApiClient.post(
        Endpoints.biometricLogin,
        body: {
          'userId': storedUserId,
          'deviceId': _deviceId,
        },
        auth: false,
      );

      if (res.success && res.data?['token'] != null) {
        await _handleLoginResponse(res.data!);
        if (res.data?['biometricToken'] != null) {
          await LocalStorageService.saveBiometricToken(
              res.data!['biometricToken'] as String);
        }
        _isLoading = false;
        notifyListeners();
        return true;
      }

      // If network error, fall through to offline
      if (!_isNetworkError(res.message)) {
        // Server explicitly rejected - don't fall through
        _error = res.message ?? 'Biometric login failed. Please use password.';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    }

    // Step 3: Offline fallback — biometric passed locally, use cached user
    // Always restore the stored access token to ApiClient so API calls work
    final storedToken = LocalStorageService.accessToken;
    if (storedToken != null && storedToken.isNotEmpty) {
      await ApiClient.setToken(storedToken);
    }

    final cachedUser = LocalStorageService.cachedUserJson;
    if (cachedUser != null) {
      _user = UserModel.fromJson(cachedUser);
      _isAuthenticated = true;
      _isLocked = false;
      _hasCompletedFirstLogin = true;
      await LocalStorageService.updateLastActiveTime();

      // If we have a valid token, try refreshing it in the background
      if (storedToken != null && storedToken.isNotEmpty) {
        _tryRefreshToken().then((_) => notifyListeners());
      }

      _isLoading = false;
      notifyListeners();
      return true;
    }

    // If we have a stored access token but no cached user, try profile fetch
    if (ApiClient.hasToken) {
      final res = await ApiClient.get(Endpoints.userProfile);
      if (res.success && res.data?['user'] != null) {
        _user = UserModel.fromJson(
            res.data!['user'] as Map<String, dynamic>);
        await LocalStorageService.saveUserJson(
            res.data!['user'] as Map<String, dynamic>);
        _isAuthenticated = true;
        _isLocked = false;
        _hasCompletedFirstLogin = true;
        await LocalStorageService.updateLastActiveTime();
        _isLoading = false;
        notifyListeners();
        return true;
      }
    }

    _error = 'Please login with password first to enable biometric';
    _isLoading = false;
    notifyListeners();
    return false;
  }

  /// Unlock the app after auto-lock (uses biometric if enabled, else password).
  Future<bool> unlockApp() async {
    if (_isBiometricEnabled && _isBiometricAvailable) {
      final success = await authenticateWithBiometric();
      if (success) {
        _isLocked = false;
        notifyListeners();
        return true;
      }
      return false;
    }
    // No biometric - need password login
    return false;
  }

  // ─── Toggle Biometric (backend-synced) ───

  Future<bool> toggleBiometric() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final newState = !_isBiometricEnabled;

    // If enabling, verify biometric hardware first
    if (newState) {
      final available = await BiometricService.isAvailable;
      if (!available) {
        _error = 'Biometric hardware not available on this device';
        _isLoading = false;
        notifyListeners();
        return false;
      }
      // Verify user can authenticate
      final localAuth = await BiometricService.authenticate(
        reason: 'Verify fingerprint to enable biometric login',
      );
      if (!localAuth) {
        _error = 'Biometric verification failed';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    }

    final res = await ApiClient.post(
      Endpoints.biometricToggle,
      body: {
        'enabled': newState,
        'deviceId': _deviceId,
      },
    );

    if (res.success) {
      _isBiometricEnabled = newState;
      await LocalStorageService.setBiometricEnabled(newState);

      // If enabling, save biometric token & register device
      if (newState && res.data?['biometricToken'] != null) {
        await LocalStorageService.saveBiometricToken(
            res.data!['biometricToken'] as String);
        // Register this as a trusted device
        await ApiClient.post(Endpoints.registerDevice, body: {
          'deviceId': _deviceId,
          'deviceName': 'Mobile Device',
          'platform': 'android',
        });
      } else if (!newState) {
        // Disabling - clear biometric token
        await LocalStorageService.saveBiometricToken('');
      }

      _user = _user?.copyWith(biometricEnabled: newState);
    } else {
      _error = res.message ?? 'Failed to toggle biometric';
    }

    _isLoading = false;
    notifyListeners();
    return res.success;
  }

  // ─── Signup ───

  Future<bool> signup(String name, String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.signup,
      body: {'name': name, 'email': email, 'password': password},
      auth: false,
    );

    if (res.success) {
      _pendingEmail = email;
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Signup failed. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyOtp(String otp) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final email = _pendingEmail ?? '';
    final res = await ApiClient.post(
      Endpoints.verifyOtp,
      body: {'email': email, 'otp': otp},
      auth: false,
    );

    if (res.success && res.data?['token'] != null) {
      await _handleLoginResponse(res.data!);
      _pendingEmail = null;
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Invalid OTP';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> resendOtp() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final email = _pendingEmail ?? '';
    final res = await ApiClient.post(
      Endpoints.verifyOtp,
      body: {'email': email, 'resend': true},
      auth: false,
    );

    _isLoading = false;
    if (!res.success) {
      _error = res.message ?? 'Failed to resend OTP';
    }
    notifyListeners();
    return res.success;
  }

  // ─── Forgot / Reset Password ───

  Future<bool> forgotPassword(String email) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.forgotPassword,
      body: {'email': email},
      auth: false,
    );

    if (res.success) {
      _pendingEmail = email;
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Failed to send reset code';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> verifyResetOtp(String otp) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final email = _pendingEmail ?? '';
    final res = await ApiClient.post(
      Endpoints.verifyResetOtp,
      body: {'email': email, 'otp': otp},
      auth: false,
    );

    if (res.success && res.data?['resetToken'] != null) {
      _resetToken = res.data!['resetToken'] as String;
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Invalid OTP';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> resetPassword(String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.resetPassword,
      body: {
        'email': _pendingEmail ?? '',
        'resetToken': _resetToken ?? '',
        'newPassword': newPassword,
      },
      auth: false,
    );

    _isLoading = false;
    if (res.success) {
      _pendingEmail = null;
      _resetToken = null;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Failed to reset password';
      notifyListeners();
      return false;
    }
  }

  // ─── Profile ───

  Future<bool> changePassword(
      String currentPassword, String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.userChangePassword,
      body: {
        'currentPassword': currentPassword,
        'newPassword': newPassword,
      },
    );

    _isLoading = false;
    if (!res.success) {
      _error = res.message ?? 'Failed to change password';
    }
    notifyListeners();
    return res.success;
  }

  Future<bool> updateProfile(String name) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.put(
      Endpoints.userProfile,
      body: {'name': name},
    );

    if (res.success && res.data?['user'] != null) {
      _user = UserModel.fromJson(res.data!['user'] as Map<String, dynamic>);
      await LocalStorageService.saveUserJson(
          res.data!['user'] as Map<String, dynamic>);
    }
    _isLoading = false;
    notifyListeners();
    return res.success;
  }

  // ─── Token Refresh ───

  Future<bool> _tryRefreshToken() async {
    final refreshToken = LocalStorageService.refreshToken;
    if (refreshToken == null || refreshToken.isEmpty) return false;

    final res = await ApiClient.post(
      Endpoints.refresh,
      body: {'refreshToken': refreshToken},
      auth: false,
    );

    if (res.success && res.data?['token'] != null) {
      final newAccess = res.data!['token'] as String;
      final newRefresh =
          res.data?['refreshToken'] as String? ?? refreshToken;
      await ApiClient.setToken(newAccess);
      await LocalStorageService.saveTokens(
        accessToken: newAccess,
        refreshToken: newRefresh,
      );

      // Fetch user profile
      final profileRes = await ApiClient.get(Endpoints.userProfile);
      if (profileRes.success && profileRes.data?['user'] != null) {
        _user = UserModel.fromJson(
            profileRes.data!['user'] as Map<String, dynamic>);
        _isAuthenticated = true;
        _hasCompletedFirstLogin = true;
        await LocalStorageService.updateLastActiveTime();
        return true;
      }
    }
    return false;
  }

  // ─── Logout ───

  Future<void> logout() async {
    try {
      await ApiClient.post(Endpoints.logout);
    } catch (_) {}
    await _clearSession();
    notifyListeners();
  }

  Future<void> _clearSession() async {
    await ApiClient.clearToken();
    await LocalStorageService.clearTokens();
    _user = null;
    _isAuthenticated = false;
    _isLocked = false;
    _error = null;
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
