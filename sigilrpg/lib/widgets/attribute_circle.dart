import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:sigilrpg/constants/app_colors.dart';

class AttributeCircle extends StatelessWidget {
  final String label;
  final int value;
  final double size;
  final VoidCallback? onTap;
  const AttributeCircle({
    super.key,
    required this.label,
    required this.value,
    this.size = 72,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Widget circle = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
          colors: [AppColors.accent.withOpacity(0.35), AppColors.surface],
          radius: 0.9,
        ),
        boxShadow: [
          BoxShadow(
            color: AppColors.accent.withOpacity(0.25),
            blurRadius: 12,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '$value',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.w800,
                color: Colors.white,
              ),
            ),
            Text(
              label,
              style: Theme.of(
                context,
              ).textTheme.labelLarge?.copyWith(color: Colors.white70),
            ),
          ],
        ),
      ),
    );

    if (onTap != null) {
      return MouseRegion(
        cursor: SystemMouseCursors.click,
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: AppColors.seed.withOpacity(0.5),
                width: 2,
              ),
            ),
            child: circle,
          ),
        ),
      );
    }

    return circle;
  }
}
