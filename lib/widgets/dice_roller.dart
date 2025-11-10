import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/controllers/dicecontroller.dart';
import 'package:sigilrpg/widgets/custom_button.dart';
import 'package:sigilrpg/widgets/empty_state.dart';

class DiceRoller extends StatefulWidget {
  const DiceRoller({super.key});

  @override
  State<DiceRoller> createState() => _DiceRollerState();
}

class _DiceRollerState extends State<DiceRoller> {
  final TextEditingController _count = TextEditingController(text: '1');
  final TextEditingController _sides = TextEditingController(text: '20');
  final TextEditingController _mod = TextEditingController(text: '0');
  int? _lastResult;

  @override
  void dispose() {
    _count.dispose();
    _sides.dispose();
    _mod.dispose();
    super.dispose();
  }

  void _rollDice(DiceController dice) {
    final c = int.tryParse(_count.text) ?? 1;
    final s = int.tryParse(_sides.text) ?? 20;
    final m = int.tryParse(_mod.text) ?? 0;
    
    // O DiceController já cuida da vibração e notificação
    final result = dice.roll(count: c, sides: s, modifier: m);
    setState(() => _lastResult = result.total);
  }

  @override
  Widget build(BuildContext context) {
    final dice = context.watch<DiceController>();
    
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Quick presets
          _buildPresets(context, dice),
          const SizedBox(height: 24),
          
          // Custom roll
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Rolagem Customizada',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(child: _numberField('Quantidade', _count)),
                      const SizedBox(width: 12),
                      Expanded(child: _numberField('Lados', _sides)),
                      const SizedBox(width: 12),
                      Expanded(child: _numberField('Modificador', _mod)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  CustomButton(
                    label: 'Rolar Dados',
                    icon: Icons.casino,
                    onPressed: () => _rollDice(dice),
                    variant: ButtonVariant.primary,
                    isFullWidth: true,
                  ),
                ],
              ),
            ),
          ),
          
          // Last result display
          if (_lastResult != null) ...[
            const SizedBox(height: 16),
            Card(
              color: AppColors.seed.withOpacity(0.1),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Center(
                  child: Column(
                    children: [
                      Text(
                        'Último Resultado',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '$_lastResult',
                        style: Theme.of(context).textTheme.displayMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppColors.seed,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
          
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Histórico',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              if (dice.history.isNotEmpty)
                TextButton.icon(
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Limpar histórico?'),
                        content: const Text(
                          'Tem certeza que deseja limpar todo o histórico?',
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx),
                            child: const Text('Cancelar'),
                          ),
                          TextButton(
                            onPressed: () {
                              dice.clearHistory();
                              setState(() => _lastResult = null);
                              Navigator.pop(ctx);
                            },
                            child: const Text('Limpar', style: TextStyle(color: Colors.red)),
                          ),
                        ],
                      ),
                    );
                  },
                  icon: const Icon(Icons.clear_all, size: 18),
                  label: const Text('Limpar'),
                ),
            ],
          ),
          const SizedBox(height: 12),
          
          // History list
          if (dice.history.isEmpty)
            EmptyState(
              icon: Icons.history,
              title: 'Nenhuma rolagem',
              message: 'Suas rolagens aparecerão aqui',
            )
          else
            ...dice.history.asMap().entries.map((entry) {
              final i = entry.key;
              final h = entry.value;
              return Padding(
                padding: EdgeInsets.only(bottom: i < dice.history.length - 1 ? 8 : 0),
                child: Card(
                  child: ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.seed.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.casino,
                        color: AppColors.seed,
                        size: 20,
                      ),
                    ),
                    title: Text(
                      '${h.count}d${h.sides}${h.modifier != 0 ? (h.modifier > 0 ? '+${h.modifier}' : h.modifier) : ''}',
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                    subtitle: Text(
                      'Rolagens: ${h.rolls.join(', ')}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    trailing: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: AppColors.seed.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '${h.total}',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: AppColors.seed,
                            ),
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
        ],
      ),
    );
  }

  Widget _buildPresets(BuildContext context, DiceController dice) {
    final presets = [
      {'label': 'd20', 'count': 1, 'sides': 20, 'mod': 0, 'icon': Icons.sports_mma},
      {'label': '2d6', 'count': 2, 'sides': 6, 'mod': 0, 'icon': Icons.casino},
      {'label': 'd100', 'count': 1, 'sides': 100, 'mod': 0, 'icon': Icons.looks_one},
      {'label': '4d6', 'count': 4, 'sides': 6, 'mod': 0, 'icon': Icons.view_agenda},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Presets Rápidos',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: presets.map((preset) {
            return InkWell(
              onTap: () {
                // O DiceController já cuida da vibração e notificação
                final result = dice.roll(
                  count: preset['count'] as int,
                  sides: preset['sides'] as int,
                  modifier: preset['mod'] as int,
                );
                setState(() => _lastResult = result.total);
              },
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  color: AppColors.seed.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.seed.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      preset['icon'] as IconData,
                      size: 20,
                      color: AppColors.seed,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      preset['label'] as String,
                      style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.w600,
                            color: AppColors.seed,
                          ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _numberField(String label, TextEditingController c) {
    return TextField(
      controller: c,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      keyboardType: TextInputType.number,
      textAlign: TextAlign.center,
    );
  }
}
