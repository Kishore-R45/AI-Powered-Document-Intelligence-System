import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_input.dart';
import '../../widgets/common/gradient_background.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final List<TextEditingController> _otpControllers =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _otpFocusNodes = List.generate(6, (_) => FocusNode());

  String? _emailError;
  String? _passwordError;
  int _step = 0; // 0 = email, 1 = otp, 2 = new password, 3 = success

  @override
  void initState() {
    super.initState();
    // Clear any error from other auth screens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().clearError();
    });
  }

  @override
  void dispose() {
    _emailController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    for (final c in _otpControllers) {
      c.dispose();
    }
    for (final f in _otpFocusNodes) {
      f.dispose();
    }
    super.dispose();
  }

  bool _validateEmail() {
    setState(() {
      _emailError = null;
      if (_emailController.text.trim().isEmpty) {
        _emailError = 'Email is required';
      } else if (!RegExp(r'^[^@]+@[^@]+\.[^@]+')
          .hasMatch(_emailController.text.trim())) {
        _emailError = 'Enter a valid email';
      }
    });
    return _emailError == null;
  }

  Future<void> _handleSendOtp() async {
    if (!_validateEmail()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.forgotPassword(_emailController.text.trim());

    if (success && mounted) {
      setState(() => _step = 1);
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _otpFocusNodes[0].requestFocus();
      });
    }
  }

  String get _otpCode => _otpControllers.map((c) => c.text).join();

  void _handleOtpInput(int index, String value) {
    if (value.isNotEmpty && index < 5) {
      _otpFocusNodes[index + 1].requestFocus();
    }
    if (_otpCode.length == 6) {
      _handleVerifyOtp();
    }
  }

  Future<void> _handleVerifyOtp() async {
    if (_otpCode.length != 6) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.verifyResetOtp(_otpCode);

    if (success && mounted) {
      setState(() => _step = 2);
    }
  }

  Future<void> _handleResetPassword() async {
    setState(() => _passwordError = null);
    if (_newPasswordController.text.length < 8) {
      setState(() => _passwordError = 'Password must be at least 8 characters');
      return;
    }
    if (_newPasswordController.text != _confirmPasswordController.text) {
      setState(() => _passwordError = 'Passwords do not match');
      return;
    }

    final auth = context.read<AuthProvider>();
    final success = await auth.resetPassword(_newPasswordController.text);

    if (success && mounted) {
      setState(() => _step = 3);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();

    return Scaffold(
      body: GradientBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 16),

                // ─── Back Button ───
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: Theme.of(context).colorScheme.outlineVariant,
                      ),
                    ),
                    child: const Icon(Icons.arrow_back, size: 20),
                  ),
                ).animate().fadeIn(duration: 300.ms),

                const SizedBox(height: 48),

                // ─── Icon ───
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: _step == 3 ? AppTheme.success50 : AppTheme.brand50,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _step == 3
                        ? Icons.check_circle_outline
                        : _step == 1
                            ? Icons.pin_outlined
                            : _step == 2
                                ? Icons.lock_reset
                                : Icons.key_outlined,
                    size: 36,
                    color: _step == 3 ? AppTheme.success500 : AppTheme.brand600,
                  ),
                )
                    .animate()
                    .fadeIn(delay: 100.ms, duration: 400.ms)
                    .scale(begin: const Offset(0.8, 0.8), duration: 400.ms),

                const SizedBox(height: 24),

                Text(
                  _step == 0
                      ? 'Forgot Password?'
                      : _step == 1
                          ? 'Enter OTP'
                          : _step == 2
                              ? 'New Password'
                              : 'Password Reset!',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

                const SizedBox(height: 8),

                Text(
                  _step == 0
                      ? 'Enter your email and we\'ll send you a reset OTP'
                      : _step == 1
                          ? 'Enter the 6-digit code sent to ${_emailController.text.trim()}'
                          : _step == 2
                              ? 'Enter your new password'
                              : 'Your password has been reset successfully',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withOpacity(0.6),
                        height: 1.5,
                      ),
                ).animate().fadeIn(delay: 300.ms, duration: 400.ms),

                const SizedBox(height: 40),

                // ─── Error ───
                if (auth.error != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.error50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                          color: AppTheme.error500.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline,
                            color: AppTheme.error500, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            auth.error!,
                            style: const TextStyle(
                                color: AppTheme.error700, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn().shake(),

                // ─── Step 0: Email ───
                if (_step == 0) ...[
                  CustomInput(
                    label: 'Email address',
                    hint: 'you@example.com',
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icons.mail_outlined,
                    errorText: _emailError,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _handleSendOtp(),
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms).slideY(begin: 0.1),

                  const SizedBox(height: 24),

                  CustomButton(
                    text: 'Send Reset OTP',
                    onPressed: _handleSendOtp,
                    isLoading: auth.isLoading,
                    fullWidth: true,
                    size: ButtonSize.lg,
                    rightIcon: Icons.send,
                  ).animate().fadeIn(delay: 500.ms, duration: 400.ms).slideY(begin: 0.1),
                ],

                // ─── Step 1: OTP ───
                if (_step == 1) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: List.generate(6, (index) {
                      return SizedBox(
                        width: 48,
                        height: 56,
                        child: TextField(
                          controller: _otpControllers[index],
                          focusNode: _otpFocusNodes[index],
                          textAlign: TextAlign.center,
                          keyboardType: TextInputType.number,
                          maxLength: 1,
                          onChanged: (value) => _handleOtpInput(index, value),
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                          ],
                          style: Theme.of(context)
                              .textTheme
                              .titleLarge
                              ?.copyWith(fontWeight: FontWeight.w700),
                          decoration: InputDecoration(
                            counterText: '',
                            contentPadding:
                                const EdgeInsets.symmetric(vertical: 12),
                            filled: true,
                            fillColor: AppTheme.neutral50,
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide:
                                  const BorderSide(color: AppTheme.neutral300),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(8),
                              borderSide: BorderSide(
                                color: Theme.of(context).colorScheme.primary,
                                width: 2,
                              ),
                            ),
                          ),
                        ),
                      );
                    }),
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

                  const SizedBox(height: 24),

                  CustomButton(
                    text: 'Verify OTP',
                    onPressed: _handleVerifyOtp,
                    isLoading: auth.isLoading,
                    fullWidth: true,
                    size: ButtonSize.lg,
                  ).animate().fadeIn(delay: 500.ms, duration: 400.ms),
                ],

                // ─── Step 2: New Password ───
                if (_step == 2) ...[
                  CustomInput(
                    label: 'New Password',
                    hint: 'Enter new password',
                    controller: _newPasswordController,
                    obscureText: true,
                    prefixIcon: Icons.lock_outline,
                    errorText: _passwordError,
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

                  const SizedBox(height: 16),

                  CustomInput(
                    label: 'Confirm Password',
                    hint: 'Confirm new password',
                    controller: _confirmPasswordController,
                    obscureText: true,
                    prefixIcon: Icons.lock_outline,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _handleResetPassword(),
                  ).animate().fadeIn(delay: 450.ms, duration: 400.ms),

                  const SizedBox(height: 24),

                  CustomButton(
                    text: 'Reset Password',
                    onPressed: _handleResetPassword,
                    isLoading: auth.isLoading,
                    fullWidth: true,
                    size: ButtonSize.lg,
                  ).animate().fadeIn(delay: 500.ms, duration: 400.ms),
                ],

                // ─── Step 3: Success ───
                if (_step == 3) ...[
                  CustomButton(
                    text: 'Back to Login',
                    onPressed: () => Navigator.pop(context),
                    fullWidth: true,
                    size: ButtonSize.lg,
                    leftIcon: Icons.login,
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
