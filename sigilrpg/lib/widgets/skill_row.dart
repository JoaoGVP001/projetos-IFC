import 'package:flutter/material.dart';

class SkillRow extends StatelessWidget {
  final String name;
  final String attribute;
  final int bonusDice;
  final int training;
  final int others;
  final VoidCallback? onRoll;

  const SkillRow({
    super.key,
    required this.name,
    required this.attribute,
    this.bonusDice = 0,
    this.training = 0,
    this.others = 0,
    this.onRoll,
  });

  @override
  Widget build(BuildContext context) {
    final modifier =
        training + others; // simplistic; attribute mod handled elsewhere
    return ListTile(
      title: Text(name),
      subtitle: Text(
        'Atrib: $attribute  Dados+: $bonusDice  Treino: $training  Outros: $others',
      ),
      trailing: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(modifier >= 0 ? '+$modifier' : '$modifier'),
          const SizedBox(width: 8),
          IconButton(icon: const Icon(Icons.casino), onPressed: onRoll),
        ],
      ),
    );
  }
}
