import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../api/api_client.dart';
import '../api/endpoints.dart';

class AuthProvider extends ChangeNotifier {
  UserModel? _user;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  bool _isBiometricEnabled = false;
  bool _isBiometricAvailable = false;
  String? _error;
  bool _hasCompletedFirstLogin = false;
  String? _pendingEmail; // email for OTP / reset flows

  // Getters
  UserModel? get user => _user;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  bool get isBiometricEnabled => _isBiometricEnabled;
  bool get isBiometricAvailable => _isBiometricAvailable;
  String? get error => _error;
  bool get hasCompletedFirstLogin => _hasCompletedFirstLogin;
  String? get pendingEmail => _pendingEmail;

  AuthProvider() {
    _checkPersistedSession();
  }

  Future<void> _checkPersistedSession() async {
    await ApiClient.loadToken();
    if (ApiClient.hasToken) {
      // Validate token by fetching profile
      final res = await ApiClient.get(Endpoints.userProfile);
      if (res.success && res.data?['user'] != null) {
        _user = UserModel.fromJson(res.data!['user'] as Map<String, dynamic>);
        _isAuthenticated = true;
        _hasCompletedFirstLogin = true;
      } else {
        await ApiClient.clearToken();
      }
    }
    _isBiometricAvailable = true;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final res = await ApiClient.post(
      Endpoints.login,
      body: {'email': email, 'password': password},
      auth: false,
    );

    if (res.success && res.data?['token'] != null) {
      await ApiClient.setToken(res.data!['token'] as String);
      if (res.data!['user'] != null) {
        _user = UserModel.fromJson(res.data!['user'] as Map<String, dynamic>);
      }
      _isAuthenticated = true;
      _hasCompletedFirstLogin = true;
      _isLoading = false;
      notifyListeners();
      return true;
    } else {
      _error = res.message ?? 'Invalid email or password';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

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
      await ApiClient.setToken(res.data!['token'] as String);
      if (res.data!['user'] != null) {
        _user = UserModel.fromJson(res.data!['user'] as Map<String, dynamic>);
      }
      _isAuthenticated = true;
      _hasCompletedFirstLogin = true;
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
      // Store reset token temporarily
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

  String? _resetToken;

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

  Future<bool> changePassword(String currentPassword, String newPassword) async {
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
    }
    _isLoading = false;
    notifyListeners();
    return res.success;
  }

  Future<bool> authenticateWithBiometric() async {
    _isLoading = true;
    notifyListeners();

    // Biometric only works if already logged in (token stored)
    if (ApiClient.hasToken) {
      final res = await ApiClient.get(Endpoints.userProfile);
      if (res.success && res.data?['user'] != null) {
        _user = UserModel.fromJson(res.data!['user'] as Map<String, dynamic>);
        _isAuthenticated = true;
        _isLoading = false;
        notifyListeners();
        return true;
      }
    }
    _isLoading = false;
    notifyListeners();
    return false;
  }

  void toggleBiometric() {
    _isBiometricEnabled = !_isBiometricEnabled;
    notifyListeners();
  }

  Future<void> logout() async {
    try {
      await ApiClient.post(Endpoints.logout);
    } catch (_) {}
    await ApiClient.clearToken();
    _user = null;
    _isAuthenticated = false;
    _error = null;
    notifyListeners();
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
