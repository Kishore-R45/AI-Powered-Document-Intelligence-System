import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_input.dart';
import '../../widgets/common/gradient_background.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  bool _showPassword = false;
  bool _showConfirmPassword = false;
  String? _nameError;
  String? _emailError;
  String? _passwordError;
  String? _confirmPasswordError;

  double _passwordStrength = 0;

  @override
  void initState() {
    super.initState();
    _passwordController.addListener(_calculatePasswordStrength);
    // Clear any error from other auth screens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<AuthProvider>().clearError();
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _calculatePasswordStrength() {
    final password = _passwordController.text;
    double strength = 0;
    if (password.length >= 8) strength += 0.25;
    if (password.contains(RegExp(r'[A-Z]'))) strength += 0.25;
    if (password.contains(RegExp(r'[0-9]'))) strength += 0.25;
    if (password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) strength += 0.25;
    setState(() => _passwordStrength = strength);
  }

  Color _getStrengthColor() {
    if (_passwordStrength <= 0.25) return AppTheme.error500;
    if (_passwordStrength <= 0.5) return AppTheme.warning500;
    if (_passwordStrength <= 0.75) return const Color(0xFFF79009);
    return AppTheme.success500;
  }

  String _getStrengthLabel() {
    if (_passwordStrength <= 0.25) return 'Weak';
    if (_passwordStrength <= 0.5) return 'Fair';
    if (_passwordStrength <= 0.75) return 'Good';
    return 'Strong';
  }

  bool _validate() {
    bool valid = true;
    setState(() {
      _nameError = null;
      _emailError = null;
      _passwordError = null;
      _confirmPasswordError = null;

      if (_nameController.text.trim().isEmpty) {
        _nameError = 'Name is required';
        valid = false;
      } else if (_nameController.text.trim().length < 2) {
        _nameError = 'Name must be at least 2 characters';
        valid = false;
      }

      if (_emailController.text.trim().isEmpty) {
        _emailError = 'Email is required';
        valid = false;
      } else if (!RegExp(r'^[^@]+@[^@]+\.[^@]+').hasMatch(_emailController.text.trim())) {
        _emailError = 'Enter a valid email';
        valid = false;
      }

      if (_passwordController.text.isEmpty) {
        _passwordError = 'Password is required';
        valid = false;
      } else if (_passwordController.text.length < 8) {
        _passwordError = 'Password must be at least 8 characters';
        valid = false;
      }

      if (_confirmPasswordController.text != _passwordController.text) {
        _confirmPasswordError = 'Passwords do not match';
        valid = false;
      }
    });
    return valid;
  }

  Future<void> _handleSignup() async {
    if (!_validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.signup(
      _nameController.text.trim(),
      _emailController.text.trim(),
      _passwordController.text,
    );

    if (success && mounted) {
      Navigator.pushNamed(context, '/otp-verification');
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

                const SizedBox(height: 32),

                // ─── Header ───
                Text(
                  'Create Account',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

                const SizedBox(height: 8),

                Text(
                  'Start securing your documents today',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withOpacity(0.6),
                      ),
                ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

                const SizedBox(height: 32),

                // ─── Error Message ───
                if (auth.error != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: AppTheme.error50,
                      borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                      border: Border.all(color: AppTheme.error500.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: AppTheme.error500, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            auth.error!,
                            style: const TextStyle(color: AppTheme.error700, fontSize: 13),
                          ),
                        ),
                      ],
                    ),
                  ).animate().fadeIn().slideY(begin: -0.2),

                // ─── Name Field ───
                CustomInput(
                  label: 'Full Name',
                  hint: 'John Doe',
                  controller: _nameController,
                  prefixIcon: Icons.person_outlined,
                  errorText: _nameError,
                  textInputAction: TextInputAction.next,
                ).animate().fadeIn(delay: 300.ms, duration: 400.ms).slideY(begin: 0.1),

                const SizedBox(height: 16),

                // ─── Email Field ───
                CustomInput(
                  label: 'Email address',
                  hint: 'you@example.com',
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.mail_outlined,
                  errorText: _emailError,
                  textInputAction: TextInputAction.next,
                ).animate().fadeIn(delay: 400.ms, duration: 400.ms).slideY(begin: 0.1),

                const SizedBox(height: 16),

                // ─── Password Field ───
                CustomInput(
                  label: 'Password',
                  hint: 'Create a strong password',
                  controller: _passwordController,
                  obscureText: !_showPassword,
                  prefixIcon: Icons.lock_outlined,
                  errorText: _passwordError,
                  textInputAction: TextInputAction.next,
                  suffixWidget: IconButton(
                    icon: Icon(
                      _showPassword ? Icons.visibility_off : Icons.visibility,
                      size: 20,
                    ),
                    onPressed: () => setState(() => _showPassword = !_showPassword),
                  ),
                ).animate().fadeIn(delay: 500.ms, duration: 400.ms).slideY(begin: 0.1),

                // ─── Password Strength ───
                if (_passwordController.text.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: _passwordStrength,
                            backgroundColor: Theme.of(context)
                                .colorScheme
                                .outlineVariant,
                            valueColor: AlwaysStoppedAnimation(_getStrengthColor()),
                            minHeight: 4,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        _getStrengthLabel(),
                        style: TextStyle(
                          color: _getStrengthColor(),
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ],

                const SizedBox(height: 16),

                // ─── Confirm Password Field ───
                CustomInput(
                  label: 'Confirm Password',
                  hint: 'Re-enter your password',
                  controller: _confirmPasswordController,
                  obscureText: !_showConfirmPassword,
                  prefixIcon: Icons.lock_outlined,
                  errorText: _confirmPasswordError,
                  textInputAction: TextInputAction.done,
                  onSubmitted: (_) => _handleSignup(),
                  suffixWidget: IconButton(
                    icon: Icon(
                      _showConfirmPassword ? Icons.visibility_off : Icons.visibility,
                      size: 20,
                    ),
                    onPressed: () =>
                        setState(() => _showConfirmPassword = !_showConfirmPassword),
                  ),
                ).animate().fadeIn(delay: 600.ms, duration: 400.ms).slideY(begin: 0.1),

                const SizedBox(height: 32),

                // ─── Signup Button ───
                CustomButton(
                  text: 'Create Account',
                  onPressed: _handleSignup,
                  isLoading: auth.isLoading,
                  fullWidth: true,
                  size: ButtonSize.lg,
                  rightIcon: Icons.arrow_forward,
                ).animate().fadeIn(delay: 700.ms, duration: 400.ms).slideY(begin: 0.1),

                // const SizedBox(height: 12),

                // // ─── OTP Note ───
                // Row(
                //   mainAxisAlignment: MainAxisAlignment.center,
                //   children: [
                //     Icon(
                //       Icons.verified_user_outlined,
                //       size: 14,
                //       color: Theme.of(context).colorScheme.onSurface.withOpacity(0.45),
                //     ),
                //     const SizedBox(width: 6),
                //     Text(
                //       'An OTP will be sent to verify your email',
                //       style: Theme.of(context).textTheme.bodySmall?.copyWith(
                //             color: Theme.of(context)
                //                 .colorScheme
                //                 .onSurface
                //                 .withOpacity(0.45),
                //           ),
                //     ),
                //   ],
                // ).animate().fadeIn(delay: 750.ms, duration: 400.ms),

                const SizedBox(height: 24),

                // ─── Login Link ───
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Already have an account? ',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Theme.of(context)
                                .colorScheme
                                .onSurface
                                .withOpacity(0.6),
                          ),
                    ),
                    GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Text(
                        'Sign In',
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ).animate().fadeIn(delay: 800.ms, duration: 400.ms),

                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
