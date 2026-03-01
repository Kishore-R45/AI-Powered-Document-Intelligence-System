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
    // Cap delay so items further down the list don't appear too late
    final ms = (30 * index).clamp(0, 150);
    final itemDelay = delay ?? Duration(milliseconds: ms);

    return child
        .animate()
        .fadeIn(delay: itemDelay, duration: 150.ms)
        .slideY(
          begin: 0.06,
          end: 0,
          delay: itemDelay,
          duration: 150.ms,
          curve: Curves.easeOutCubic,
        );
  }
}
