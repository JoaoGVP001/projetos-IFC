class Skill {
  final String id;
  final String characterId;
  final String name;
  final String attribute; // AGI, INT, VIG, PRE, FOR
  final int bonusDice; // número de dados bônus
  final int training; // valor de treino
  final int others; // outros modificadores
  final String? description;

  const Skill({
    required this.id,
    required this.characterId,
    required this.name,
    required this.attribute,
    this.bonusDice = 0,
    this.training = 0,
    this.others = 0,
    this.description,
  });

  factory Skill.fromJson(Map<String, dynamic> json) {
    return Skill(
      id: json['id'].toString(),
      characterId: json['character_id'].toString(),
      name: json['name'] as String? ?? '',
      attribute: json['attribute'] as String? ?? 'AGI',
      bonusDice: (json['bonus_dice'] as num?)?.toInt() ?? 0,
      training: (json['training'] as num?)?.toInt() ?? 0,
      others: (json['others'] as num?)?.toInt() ?? 0,
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'attribute': attribute,
      'bonus_dice': bonusDice,
      'training': training,
      'others': others,
      if (description != null) 'description': description,
    };
  }
}
