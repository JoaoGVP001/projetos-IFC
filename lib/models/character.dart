class Character {
  final String id;
  final String name;
  final String playerName;
  final String origin;
  final String characterClass;
  final int nex;
  final String? avatarUrl;
  final CharacterAttributes attributes;
  final CharacterDetails details;

  const Character({
    required this.id,
    required this.name,
    required this.playerName,
    required this.origin,
    required this.characterClass,
    required this.nex,
    this.avatarUrl,
    required this.attributes,
    required this.details,
  });
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
}
