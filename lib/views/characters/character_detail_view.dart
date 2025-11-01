import 'package:flutter/material.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/widgets/attribute_circle.dart';
import 'package:sigilrpg/widgets/health_bar.dart';

class CharacterDetailView extends StatelessWidget {
  final Character character;
  const CharacterDetailView({super.key, required this.character});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 5,
      child: Scaffold(
        appBar: AppBar(
          title: Text(character.name),
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              tooltip: 'Editar Atributos',
              onPressed: () => Navigator.pushNamed(
                context,
                '/characters/attributes/edit',
                arguments: character.id,
              ),
            ),
          ],
          bottom: const TabBar(
            isScrollable: true,
            tabs: [
              Tab(text: 'Combate'),
              Tab(text: 'Habilidades'),
              Tab(text: 'Rituais'),
              Tab(text: 'Inventário'),
              Tab(text: 'Descrição'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _CombatTab(character: character),
            const Center(child: Text('Habilidades (placeholder)')),
            const Center(child: Text('Rituais (placeholder)')),
            const Center(child: Text('Inventário (placeholder)')),
            const Center(child: Text('Descrição (placeholder)')),
          ],
        ),
      ),
    );
  }
}

class _CombatTab extends StatelessWidget {
  final Character character;
  const _CombatTab({required this.character});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              AttributeCircle(label: 'AGI', value: character.attributes.agilidade),
              AttributeCircle(label: 'INT', value: character.attributes.intelecto),
              AttributeCircle(label: 'VIG', value: character.attributes.vigor),
              AttributeCircle(label: 'PRE', value: character.attributes.presenca),
              AttributeCircle(label: 'FOR', value: character.attributes.forca),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                HealthBar(label: 'PV', current: 20, max: 30),
                SizedBox(height: 12),
                HealthBar(
                  label: 'PE',
                  current: 8,
                  max: 12,
                  color: Colors.blueAccent,
                ),
                SizedBox(height: 12),
                HealthBar(
                  label: 'PS',
                  current: 10,
                  max: 15,
                  color: Colors.purpleAccent,
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'NEX: ${character.nex}%',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: AppColors.seed,
                          ),
                    ),
                    ElevatedButton.icon(
                      onPressed: () => Navigator.pushNamed(
                        context,
                        '/characters/attributes/edit',
                        arguments: character.id,
                      ),
                      icon: const Icon(Icons.edit, size: 18),
                      label: const Text('Editar'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.seed,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Text(
                  'Defesa: ${10 + character.attributes.agilidade}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                Text(
                  'Resistências: Física ${character.attributes.vigor}, '
                  'Balística ${character.attributes.vigor}, '
                  'Mental ${character.attributes.intelecto}',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
