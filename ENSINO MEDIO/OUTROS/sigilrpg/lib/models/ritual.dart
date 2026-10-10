class Ritual {
  final String id;
  final String characterId;
  final String name;
  final int circle; // Círculo do ritual (1-10)
  final int cost; // Custo em PE
  final String? executionTime;
  final String? range;
  final String? duration;
  final String? resistanceTest;
  final String? description;
  final String? effect;

  const Ritual({
    required this.id,
    required this.characterId,
    required this.name,
    required this.circle,
    required this.cost,
    this.executionTime,
    this.range,
    this.duration,
    this.resistanceTest,
    this.description,
    this.effect,
  });

  factory Ritual.fromJson(Map<String, dynamic> json) {
    return Ritual(
      id: json['id'].toString(),
      characterId: json['character_id'].toString(),
      name: json['name'] as String? ?? '',
      circle: (json['circle'] as num?)?.toInt() ?? 1,
      cost: (json['cost'] as num?)?.toInt() ?? 0,
      executionTime: json['execution_time'] as String?,
      range: json['range'] as String?,
      duration: json['duration'] as String?,
      resistanceTest: json['resistance_test'] as String?,
      description: json['description'] as String?,
      effect: json['effect'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'circle': circle,
      'cost': cost,
      if (executionTime != null) 'execution_time': executionTime,
      if (range != null) 'range': range,
      if (duration != null) 'duration': duration,
      if (resistanceTest != null) 'resistance_test': resistanceTest,
      if (description != null) 'description': description,
      if (effect != null) 'effect': effect,
    };
  }
}

