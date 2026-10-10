import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';

class HealthBar extends StatelessWidget {
  final String label;
  final int current;
  final int max;
  final Color color;
  const HealthBar({
    super.key,
    required this.label,
    required this.current,
    required this.max,
    this.color = AppColors.success,
  });

  @override
  Widget build(BuildContext context) {
    final double pct = max > 0 ? (current.clamp(0, max) / max) : 0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: Theme.of(context).textTheme.labelLarge),
            Text('$current / $max'),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: pct,
            minHeight: 10,
            backgroundColor: Colors.white10,
            color: color,
          ),
        ),
      ],
    );
  }
}
