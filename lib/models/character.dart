class Character {
  final String id;
  final String name;
  final String playerName;
  final String origin;
  final String characterClass;
  final int nex;
  final String? avatarUrl;
  final String skilledIn;
  final int? userId;
  final CharacterAttributes attributes;
  final CharacterDetails details;
  
  // Sistema de Combate - Valores atuais
  final int? currentPv;
  final int? currentPe;
  final int? currentPs;

  const Character({
    required this.id,
    required this.name,
    required this.playerName,
    required this.origin,
    required this.characterClass,
    required this.nex,
    this.avatarUrl,
    required this.skilledIn,
    this.userId,
    required this.attributes,
    required this.details,
    this.currentPv,
    this.currentPe,
    this.currentPs,
  });

  factory Character.fromJson(Map<String, dynamic> json) {
    return Character(
      id: json['id'].toString(),
      name: json['name'] as String? ?? '',
      playerName: json['player_name'] as String? ?? '',
      origin: json['origin'] as String? ?? '',
      characterClass: json['character_class'] as String? ?? '',
      nex: (json['nex'] as num?)?.toInt() ?? 0,
      avatarUrl: json['avatar_url'] as String?,
      skilledIn: json['skilled_in'] as String? ?? 'Combat',
      userId: (json['user_id'] as num?)?.toInt(),
      attributes: CharacterAttributes.fromJson(json),
      details: CharacterDetails.fromJson(json),
      currentPv: (json['current_pv'] as num?)?.toInt(),
      currentPe: (json['current_pe'] as num?)?.toInt(),
      currentPs: (json['current_ps'] as num?)?.toInt(),
    );
  }
}

class CharacterDetails {
  final String? gender;
  final int? age;
  final String? appearance;
  final String? personality;
  final String? background;
  final String? objective;

  const CharacterDetails({
    this.gender,
    this.age,
    this.appearance,
    this.personality,
    this.background,
    this.objective,
  });

  factory CharacterDetails.fromJson(Map<String, dynamic> json) {
    return CharacterDetails(
      gender: json['gender'] as String?,
      age: (json['age'] as num?)?.toInt(),
      appearance: json['appearance'] as String?,
      personality: json['personality'] as String?,
      background: json['background'] as String?,
      objective: json['objective'] as String?,
    );
  }
}

class CharacterAttributes {
  final int agilidade;
  final int intelecto;
  final int vigor;
  final int presenca;
  final int forca;

  const CharacterAttributes({
    required this.agilidade,
    required this.intelecto,
    required this.vigor,
    required this.presenca,
    required this.forca,
  });

  int get total => agilidade + intelecto + vigor + presenca + forca;

  factory CharacterAttributes.fromJson(Map<String, dynamic> json) {
    return CharacterAttributes(
      agilidade: (json['agilidade'] as num?)?.toInt() ?? 1,
      intelecto: (json['intelecto'] as num?)?.toInt() ?? 1,
      vigor: (json['vigor'] as num?)?.toInt() ?? 1,
      presenca: (json['presenca'] as num?)?.toInt() ?? 1,
      forca: (json['forca'] as num?)?.toInt() ?? 1,
    );
  }
}
