import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../config/theme.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/common/custom_button.dart';
import '../../widgets/common/custom_input.dart';
import '../../widgets/auth/biometric_button.dart';
import '../../widgets/common/gradient_background.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _showPassword = false;
  String? _emailError;
  String? _passwordError;

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
    _passwordController.dispose();
    super.dispose();
  }

  bool _validate() {
    bool valid = true;
    setState(() {
      _emailError = null;
      _passwordError = null;

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
      }
    });
    return valid;
  }

  Future<void> _handleLogin() async {
    if (!_validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    if (success && mounted) {
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    }
  }

  Future<void> _handleBiometricLogin() async {
    final auth = context.read<AuthProvider>();
    final success = await auth.authenticateWithBiometric();
    if (success && mounted) {
      Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final size = MediaQuery.of(context).size;

    return Scaffold(
      body: GradientBackground(
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: SizedBox(
              height: size.height - MediaQuery.of(context).padding.top - MediaQuery.of(context).padding.bottom,
              child: Column(
                children: [
                  const Spacer(flex: 2),

                  // ─── Logo & Header ───
                  Container(
                    width: 72,
                    height: 72,
                    decoration: BoxDecoration(
                      gradient: AppTheme.primaryGradient,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.brand600.withOpacity(0.3),
                          blurRadius: 20,
                          offset: const Offset(0, 8),
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.shield_outlined,
                      color: Colors.white,
                      size: 36,
                    ),
                  )
                      .animate()
                      .fadeIn(duration: 500.ms)
                      .scale(
                        begin: const Offset(0.8, 0.8),
                        duration: 500.ms,
                        curve: Curves.easeOutBack,
                      ),

                  const SizedBox(height: 24),

                  Text(
                    'InfoVault',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ).animate().fadeIn(delay: 100.ms, duration: 400.ms),

                  const SizedBox(height: 8),

                  Text(
                    'Sign in to access your document vault',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Theme.of(context)
                              .colorScheme
                              .onSurface
                              .withOpacity(0.6),
                        ),
                  ).animate().fadeIn(delay: 200.ms, duration: 400.ms),

                  const SizedBox(height: 40),

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

                  // ─── Email Field ───
                  CustomInput(
                    label: 'Email address',
                    hint: 'you@example.com',
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    prefixIcon: Icons.mail_outlined,
                    errorText: _emailError,
                    textInputAction: TextInputAction.next,
                  ).animate().fadeIn(delay: 300.ms, duration: 400.ms).slideY(begin: 0.1),

                  const SizedBox(height: 16),

                  // ─── Password Field ───
                  CustomInput(
                    label: 'Password',
                    hint: 'Enter your password',
                    controller: _passwordController,
                    obscureText: !_showPassword,
                    prefixIcon: Icons.lock_outlined,
                    errorText: _passwordError,
                    textInputAction: TextInputAction.done,
                    onSubmitted: (_) => _handleLogin(),
                    suffixWidget: IconButton(
                      icon: Icon(
                        _showPassword ? Icons.visibility_off : Icons.visibility,
                        size: 20,
                      ),
                      onPressed: () => setState(() => _showPassword = !_showPassword),
                    ),
                  ).animate().fadeIn(delay: 400.ms, duration: 400.ms).slideY(begin: 0.1),

                  const SizedBox(height: 8),

                  // ─── Forgot Password ───
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () => Navigator.pushNamed(context, '/forgot-password'),
                      child: const Text('Forgot Password?'),
                    ),
                  ).animate().fadeIn(delay: 500.ms, duration: 400.ms),

                  const SizedBox(height: 16),

                  // ─── Login Button ───
                  CustomButton(
                    text: 'Sign In',
                    onPressed: _handleLogin,
                    isLoading: auth.isLoading,
                    fullWidth: true,
                    size: ButtonSize.lg,
                    rightIcon: Icons.arrow_forward,
                  ).animate().fadeIn(delay: 600.ms, duration: 400.ms).slideY(begin: 0.1),

                  const SizedBox(height: 16),

                  // ─── Biometric Button ───
                  if (auth.isBiometricAvailable)
                    BiometricButton(
                      onPressed: _handleBiometricLogin,
                      isLoading: auth.isLoading,
                    ).animate().fadeIn(delay: 700.ms, duration: 400.ms),

                  const Spacer(flex: 1),

                  // ─── Sign Up Link ───
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        "Don't have an account? ",
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context)
                                  .colorScheme
                                  .onSurface
                                  .withOpacity(0.6),
                            ),
                      ),
                      GestureDetector(
                        onTap: () => Navigator.pushNamed(context, '/signup'),
                        child: Text(
                          'Sign Up',
                          style: TextStyle(
                            color: Theme.of(context).colorScheme.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ).animate().fadeIn(delay: 800.ms, duration: 400.ms),

                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
