import 'package:flutter/material.dart';
import '../../config/theme.dart';

enum ButtonVariant { primary, secondary, outline, ghost, danger }
enum ButtonSize { sm, md, lg }

class CustomButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final ButtonVariant variant;
  final ButtonSize size;
  final IconData? leftIcon;
  final IconData? rightIcon;
  final bool isLoading;
  final bool fullWidth;

  const CustomButton({
    super.key,
    required this.text,
    this.onPressed,
    this.variant = ButtonVariant.primary,
    this.size = ButtonSize.md,
    this.leftIcon,
    this.rightIcon,
    this.isLoading = false,
    this.fullWidth = false,
  });

  @override
  State<CustomButton> createState() => _CustomButtonState();
}

class _CustomButtonState extends State<CustomButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.96).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  EdgeInsets _getPadding() {
    switch (widget.size) {
      case ButtonSize.sm:
        return const EdgeInsets.symmetric(horizontal: 16, vertical: 8);
      case ButtonSize.md:
        return const EdgeInsets.symmetric(horizontal: 24, vertical: 14);
      case ButtonSize.lg:
        return const EdgeInsets.symmetric(horizontal: 32, vertical: 18);
    }
  }

  double _getFontSize() {
    switch (widget.size) {
      case ButtonSize.sm:
        return 13;
      case ButtonSize.md:
        return 15;
      case ButtonSize.lg:
        return 16;
    }
  }

  double _getIconSize() {
    switch (widget.size) {
      case ButtonSize.sm:
        return 16;
      case ButtonSize.md:
        return 18;
      case ButtonSize.lg:
        return 20;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isDisabled = widget.onPressed == null || widget.isLoading;

    Color bgColor;
    Color fgColor;
    Color borderColor;

    switch (widget.variant) {
      case ButtonVariant.primary:
        bgColor = Theme.of(context).colorScheme.primary;
        fgColor = Colors.white;
        borderColor = Colors.transparent;
        break;
      case ButtonVariant.secondary:
        bgColor = isDark ? const Color(0xFF252839) : AppTheme.brand50;
        fgColor = Theme.of(context).colorScheme.primary;
        borderColor = Colors.transparent;
        break;
      case ButtonVariant.outline:
        bgColor = Colors.transparent;
        fgColor = isDark ? const Color(0xFFE2E4F0) : AppTheme.neutral700;
        borderColor = Theme.of(context).colorScheme.outline;
        break;
      case ButtonVariant.ghost:
        bgColor = Colors.transparent;
        fgColor = Theme.of(context).colorScheme.primary;
        borderColor = Colors.transparent;
        break;
      case ButtonVariant.danger:
        bgColor = AppTheme.error500;
        fgColor = Colors.white;
        borderColor = Colors.transparent;
        break;
    }

    if (isDisabled) {
      bgColor = bgColor.withOpacity(0.5);
      fgColor = fgColor.withOpacity(0.5);
    }

    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: child,
        );
      },
      child: SizedBox(
        width: widget.fullWidth ? double.infinity : null,
        child: GestureDetector(
          onTapDown: isDisabled ? null : (_) => _controller.forward(),
          onTapUp: isDisabled ? null : (_) => _controller.reverse(),
          onTapCancel: isDisabled ? null : () => _controller.reverse(),
          child: Material(
            color: bgColor,
            borderRadius: BorderRadius.circular(AppTheme.radiusSm),
            child: InkWell(
              onTap: isDisabled ? null : widget.onPressed,
              borderRadius: BorderRadius.circular(AppTheme.radiusSm),
              child: Container(
                padding: _getPadding(),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(AppTheme.radiusSm),
                  border: Border.all(color: borderColor),
                ),
                child: Row(
                  mainAxisSize: widget.fullWidth ? MainAxisSize.max : MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (widget.isLoading)
                      SizedBox(
                        height: _getIconSize(),
                        width: _getIconSize(),
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: fgColor,
                        ),
                      )
                    else ...[
                      if (widget.leftIcon != null) ...[
                        Icon(widget.leftIcon, size: _getIconSize(), color: fgColor),
                        const SizedBox(width: 8),
                      ],
                      Text(
                        widget.text,
                        style: TextStyle(
                          color: fgColor,
                          fontSize: _getFontSize(),
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (widget.rightIcon != null) ...[
                        const SizedBox(width: 8),
                        Icon(widget.rightIcon, size: _getIconSize(), color: fgColor),
                      ],
                    ],
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
