import 'dart:math';

class DiceRollResult {
  final List<int> rolls;
  final int total;
  final int count;
  final int sides;
  final int modifier;
  
  const DiceRollResult({
    required this.rolls,
    required this.total,
    required this.count,
    required this.sides,
    this.modifier = 0,
  });
}

class Dice {
  static final Random _rng = Random();

  static DiceRollResult roll({
    required int count,
    required int sides,
    int modifier = 0,
  }) {
    final List<int> rolls = List.generate(
      count,
      (_) => _rng.nextInt(sides) + 1,
    );
    final int sum = rolls.fold(0, (a, b) => a + b) + modifier;
    return DiceRollResult(
      rolls: rolls,
      total: sum,
      count: count,
      sides: sides,
      modifier: modifier,
    );
  }

  static DiceRollResult d20({int modifier = 0}) =>
      roll(count: 1, sides: 20, modifier: modifier);
}
