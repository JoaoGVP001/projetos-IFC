import 'package:flutter/foundation.dart';
import 'package:sigilrpg/utils/dice.dart';
import 'package:sigilrpg/services/vibration_service.dart';
import 'package:sigilrpg/services/notification_service.dart';

class DiceController extends ChangeNotifier {
  final List<DiceRollResult> _history = <DiceRollResult>[];
  final VibrationService _vibration = VibrationService();
  final NotificationService _notification = NotificationService();

  List<DiceRollResult> get history => List.unmodifiable(_history);

  /// Rola um d20 com vibração e notificação
  DiceRollResult rollD20({int modifier = 0}) {
    // Vibração antes de rolar (feedback tátil)
    _vibration.mediumImpact();
    
    final result = Dice.d20(modifier: modifier);
    _history.insert(0, result);
    
    // Vibração especial para crítico (20) ou falha crítica (1)
    if (result.rolls.first == 20) {
      _vibration.vibratePattern([0, 100, 50, 100, 50, 150]);
    } else if (result.rolls.first == 1) {
      _vibration.heavyImpact();
    }
    
    // Notificação com resultado
    _showDiceNotification(
      diceNotation: '1d20${modifier != 0 ? (modifier > 0 ? '+$modifier' : modifier) : ''}',
      result: result,
    );
    
    notifyListeners();
    return result;
  }

  /// Rola dados customizados com vibração e notificação
  DiceRollResult roll({
    required int count,
    required int sides,
    int modifier = 0,
  }) {
    // Vibração antes de rolar
    _vibration.mediumImpact();
    
    final result = Dice.roll(count: count, sides: sides, modifier: modifier);
    _history.insert(0, result);
    
    // Vibração especial para resultados altos ou baixos
    final maxPossible = (count * sides) + modifier;
    final minPossible = count + modifier;
    final percentage = (result.total - minPossible) / (maxPossible - minPossible);
    
    if (percentage >= 0.9) {
      // Resultado muito alto - vibração dupla
      _vibration.vibratePattern([0, 100, 50, 100]);
    } else if (percentage <= 0.1) {
      // Resultado muito baixo - vibração pesada
      _vibration.heavyImpact();
    }
    
    // Notificação com resultado
    _showDiceNotification(
      diceNotation: '${count}d$sides${modifier != 0 ? (modifier > 0 ? '+$modifier' : modifier) : ''}',
      result: result,
    );
    
    notifyListeners();
    return result;
  }

  /// Mostra notificação com o resultado do dado
  Future<void> _showDiceNotification({
    required String diceNotation,
    required DiceRollResult result,
  }) async {
    // Inicializa o serviço de notificação se necessário
    await _notification.initialize();
    
    // Formata a mensagem
    String body;
    if (result.count == 1) {
      // Um único dado
      body = 'Resultado: ${result.total}';
      if (result.modifier != 0) {
        body += ' (${result.rolls.first}${result.modifier > 0 ? '+${result.modifier}' : result.modifier})';
      }
    } else {
      // Múltiplos dados
      final rollsStr = result.rolls.join(' + ');
      body = 'Resultado: ${result.total}';
      if (result.modifier != 0) {
        body += '\n($rollsStr${result.modifier > 0 ? '+${result.modifier}' : result.modifier})';
      } else {
        body += '\n($rollsStr)';
      }
    }
    
    // Emoji especial para críticos
    String emoji = '🎲';
    if (result.count == 1 && result.rolls.first == result.sides) {
      emoji = '🔥'; // Crítico máximo
    } else if (result.count == 1 && result.rolls.first == 1) {
      emoji = '💥'; // Falha crítica
    }
    
    await _notification.showNotification(
      id: DateTime.now().millisecondsSinceEpoch % 100000, // ID único baseado em timestamp
      title: '$emoji $diceNotation',
      body: body,
      payload: 'dice_result_${result.total}',
    );
  }

  void clearHistory() {
    _history.clear();
    notifyListeners();
  }
}
