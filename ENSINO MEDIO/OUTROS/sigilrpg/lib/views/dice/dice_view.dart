import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sigilrpg/constants/app_colors.dart';
import 'package:sigilrpg/controllers/dicecontroller.dart';
import 'package:sigilrpg/widgets/dice_roller.dart';
import 'package:sigilrpg/widgets/custom_button.dart';

class DiceView extends StatelessWidget {
  const DiceView({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => DiceController(),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Rolador de Dados'),
          actions: [
            Consumer<DiceController>(
              builder: (context, controller, _) {
                if (controller.history.isEmpty) return const SizedBox.shrink();
                return IconButton(
                  icon: const Icon(Icons.clear_all),
                  tooltip: 'Limpar histórico',
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Limpar histórico?'),
                        content: const Text(
                          'Tem certeza que deseja limpar todo o histórico de rolagens?',
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx),
                            child: const Text('Cancelar'),
                          ),
                          TextButton(
                            onPressed: () {
                              controller.clearHistory();
                              Navigator.pop(ctx);
                            },
                            child: const Text('Limpar', style: TextStyle(color: Colors.red)),
                          ),
                        ],
                      ),
                    );
                  },
                );
              },
            ),
          ],
        ),
        body: const SafeArea(
          child: Padding(padding: EdgeInsets.all(16), child: DiceRoller()),
        ),
      ),
    );
  }
}
