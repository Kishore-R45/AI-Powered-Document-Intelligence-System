import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class AnimatedListItem extends StatelessWidget {
  final Widget child;
  final int index;
  final Duration? delay;

  const AnimatedListItem({
    super.key,
    required this.child,
    required this.index,
    this.delay,
  });

  @override
  Widget build(BuildContext context) {
    final itemDelay = delay ?? Duration(milliseconds: 50 * index);

    return child
        .animate()
        .fadeIn(delay: itemDelay, duration: 300.ms)
        .slideY(
          begin: 0.1,
          end: 0,
          delay: itemDelay,
          duration: 300.ms,
          curve: Curves.easeOutCubic,
        );
  }
}
