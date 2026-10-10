import 'package:flutter/material.dart';
import 'package:sigilrpg/models/character.dart';

class CharacterDescriptionTab extends StatelessWidget {
  final Character character;
  const CharacterDescriptionTab({super.key, required this.character});

  @override
  Widget build(BuildContext context) {
    final details = character.details;
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (details.gender != null)
            _DescriptionSection(
              title: 'Gênero',
              content: details.gender!,
              icon: Icons.person,
            ),
          if (details.age != null)
            _DescriptionSection(
              title: 'Idade',
              content: '${details.age} anos',
              icon: Icons.cake,
            ),
          if (details.appearance != null && details.appearance!.isNotEmpty)
            _DescriptionSection(
              title: 'Aparência',
              content: details.appearance!,
              icon: Icons.face,
            ),
          if (details.personality != null && details.personality!.isNotEmpty)
            _DescriptionSection(
              title: 'Personalidade',
              content: details.personality!,
              icon: Icons.psychology,
            ),
          if (details.background != null && details.background!.isNotEmpty)
            _DescriptionSection(
              title: 'Histórico',
              content: details.background!,
              icon: Icons.history,
            ),
          if (details.objective != null && details.objective!.isNotEmpty)
            _DescriptionSection(
              title: 'Objetivo',
              content: details.objective!,
              icon: Icons.flag,
            ),
          if (details.gender == null &&
              details.age == null &&
              (details.appearance == null || details.appearance!.isEmpty) &&
              (details.personality == null || details.personality!.isEmpty) &&
              (details.background == null || details.background!.isEmpty) &&
              (details.objective == null || details.objective!.isEmpty))
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.description, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text(
                    'Nenhuma descrição',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text('Edite o personagem para adicionar informações'),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

class _DescriptionSection extends StatelessWidget {
  final String title;
  final String content;
  final IconData icon;

  const _DescriptionSection({
    required this.title,
    required this.content,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              content,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }
}

