import 'package:flutter/material.dart';
import '../../config/theme.dart';

class GradientBackground extends StatelessWidget {
  final Widget child;
  final bool useGradient;

  const GradientBackground({
    super.key,
    required this.child,
    this.useGradient = true,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (!useGradient) return child;

    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isDark
              ? [
                  const Color(0xFF0F1120),
                  const Color(0xFF151831),
                  const Color(0xFF0F1120),
                ]
              : [
                  AppTheme.brand50,
                  Colors.white,
                  const Color(0xFFF6F7F9),
                ],
        ),
      ),
      child: child,
    );
  }
}
