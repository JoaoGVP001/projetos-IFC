import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/controllers/character_draft_controller.dart';
import 'package:sigilrpg/views/characters/character_create_wizard_routes.dart';

class CharacterCreateAttributesView extends StatelessWidget {
  const CharacterCreateAttributesView({super.key});

  @override
  Widget build(BuildContext context) {
    final draft = context.watch<CharacterDraftController>();
    return Scaffold(
      appBar: AppBar(title: const Text('Criar Personagem · Atributos')),
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
                'Todos os atributos começam em 1 e você recebe 4 pontos para distribuir. Pode reduzir para 0 para ganhar +1 ponto. Máximo inicial por atributo: 3.',
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Pontos disponíveis: ${draft.pointsAvailable >= 0 ? draft.pointsAvailable : 0}',
            ),
            const SizedBox(height: 8),
            _attrRow(
              context,
              'AGI',
              draft.agilidade,
              (v) => draft.setAttribute('AGI', v),
            ),
            _attrRow(
              context,
              'INT',
              draft.intelecto,
              (v) => draft.setAttribute('INT', v),
            ),
            _attrRow(
              context,
              'VIG',
              draft.vigor,
              (v) => draft.setAttribute('VIG', v),
            ),
            _attrRow(
              context,
              'PRE',
              draft.presenca,
              (v) => draft.setAttribute('PRE', v),
            ),
            _attrRow(
              context,
              'FOR',
              draft.forca,
              (v) => draft.setAttribute('FOR', v),
            ),
            const Spacer(),
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
                      if (!draft.validateAttributes()) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Distribua até o limite de pontos.'),
                          ),
                        );
                        return;
                      }
                      Navigator.pushNamed(
                        context,
                        CharacterCreateRoutes.origin,
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

  Widget _attrRow(
    BuildContext context,
    String label,
    int value,
    ValueChanged<int> onChanged,
  ) {
    return Row(
      children: [
        SizedBox(width: 48, child: Text(label)),
        Expanded(
          child: Slider(
            min: 0,
            max: 3,
            divisions: 3,
            label: '$value',
            value: value.toDouble(),
            onChanged: (v) => onChanged(v.round()),
          ),
        ),
        SizedBox(width: 32, child: Text('$value', textAlign: TextAlign.end)),
      ],
    );
  }
}
