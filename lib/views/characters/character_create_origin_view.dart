import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/models/character_origin.dart';
import 'package:sigilrpg/views/characters/character_create_wizard_routes.dart';

class CharacterCreateOriginView extends StatelessWidget {
  const CharacterCreateOriginView({super.key});

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem · Origem')),
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
              child: const Text(
                'Sua origem define seu passado antes da Ordem.',
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: CharacterOrigins.allOrigins.length,
                itemBuilder: (context, index) {
                  final origin = CharacterOrigins.allOrigins[index];
                  final isSelected = draft.selectedOrigin?.name == origin.name;
                  return Card(
                    margin: const EdgeInsets.only(bottom: 12),
                    child: InkWell(
                      onTap: () => draft.chooseOrigin(origin),
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
                                    origin.name,
                                    style: Theme.of(context)
                                        .textTheme
                                        .titleLarge
                                        ?.copyWith(fontWeight: FontWeight.bold),
                                  ),
                                ),
                                if (isSelected)
                                  Icon(
                                    Icons.check_circle,
                                    color: Theme.of(
                                      context,
                                    ).colorScheme.primary,
                                  ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(origin.description),
                            const SizedBox(height: 8),
                            Text(
                              'Perícias: ${origin.trainedSkills.join(', ')}',
                            ),
                            const SizedBox(height: 4),
                            Text('Poder: ${origin.powerName}'),
                            Text(
                              origin.powerDescription,
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(fontStyle: FontStyle.italic),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
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
                      if (!draft.validateOrigin()) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Selecione uma origem.'),
                          ),
                        );
                        return;
                      }
                      Navigator.pushNamed(context, CharacterCreateRoutes.clazz);
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
}
