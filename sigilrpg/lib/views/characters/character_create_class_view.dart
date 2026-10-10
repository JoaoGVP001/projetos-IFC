import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/models/character_class.dart';
import 'package:sigilrpg/views/characters/character_create_wizard_routes.dart';

class CharacterCreateClassView extends StatelessWidget {
  const CharacterCreateClassView({super.key});

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem · Classe')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surfaceVariant,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text('Escolha a classe do agente.'),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                children: [
                  ...CharacterClasses.allClasses.map(
                    (classe) => _buildClassCard(context, draft, classe),
                  ),
                ],
              ),
            ),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    child: const Text('Voltar'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      if (!draft.validateClass()) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Selecione uma classe.'),
                          ),
                        );
                        return;
                      }
                      Navigator.pushNamed(
                        context,
                        CharacterCreateRoutes.details,
                      );
                    },
                    child: const Text('Continuar'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildClassCard(
    BuildContext context,
    CharacterDraftController draft,
    CharacterClass classe,
  ) {
    final isSelected = draft.selectedClass?.name == classe.name;
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => draft.chooseClass(classe),
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            border: isSelected
                ? Border.all(
                    color: Theme.of(context).colorScheme.primary,
                    width: 2,
                  )
                : null,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      classe.name,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  if (isSelected)
                    Icon(
                      Icons.check_circle,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(classe.description),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildStatInfo(
                      context,
                      'PV Iniciais',
                      '${classe.stats.initialHealth}+VIGOR',
                    ),
                  ),
                  Expanded(
                    child: _buildStatInfo(
                      context,
                      'PE Iniciais',
                      '${classe.stats.initialEffort}+PRESENÇA',
                    ),
                  ),
                  Expanded(
                    child: _buildStatInfo(
                      context,
                      'SAN Inicial',
                      '${classe.stats.initialSanity}',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatInfo(BuildContext context, String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(
          value,
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}
