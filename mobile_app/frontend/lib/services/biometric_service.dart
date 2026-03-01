import 'package:local_auth/local_auth.dart';

/// Wraps the local_auth plugin for biometric authentication.
class BiometricService {
  static final LocalAuthentication _auth = LocalAuthentication();

  BiometricService._();

  /// Check whether biometric hardware is available on this device.
  static Future<bool> get isAvailable async {
    try {
      final canCheck = await _auth.canCheckBiometrics;
      final isDeviceSupported = await _auth.isDeviceSupported();
      return canCheck || isDeviceSupported;
    } catch (_) {
      return false;
    }
  }

  /// Returns the list of enrolled biometric types (fingerprint, face, iris).
  static Future<List<BiometricType>> get enrolledBiometrics async {
    try {
      return await _auth.getAvailableBiometrics();
    } catch (_) {
      return [];
    }
  }

  /// Prompt the user for biometric authentication.
  /// Returns true if the user successfully authenticated.
  static Future<bool> authenticate({
    String reason = 'Authenticate to access InfoVault',
  }) async {
    try {
      return await _auth.authenticate(
        localizedReason: reason,
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false, // allow PIN/pattern fallback
        ),
      );
    } catch (_) {
      return false;
    }
  }
}
