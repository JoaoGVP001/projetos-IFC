import 'package:flutter/foundation.dart';
import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/models/character_class.dart';
import 'package:sigilrpg/models/character_origin.dart';
import 'package:sigilrpg/services/characters_service.dart';

class CharacterDraftController extends ChangeNotifier {
  CharacterDraftController({CharactersService? service})
    : _service = service ?? CharactersService();

  final CharactersService _service;

  // Basics
  String name = '';
  String playerName = '';
  int nex = 5;
  String? avatarUrl;

  // Attributes
  int agilidade = 1;
  int intelecto = 1;
  int vigor = 1;
  int presenca = 1;
  int forca = 1;

  int get attributesTotal => agilidade + intelecto + vigor + presenca + forca;
  int get pointsAvailable => 4 - (attributesTotal - 5);

  // Origin and Class
  CharacterOrigin? selectedOrigin;
  CharacterClass? selectedClass;
  String skilledIn = 'Combat'; // Habilidade padrão

  // Details
  String? gender;
  int? age;
  String? appearance;
  String? personality;
  String? background;
  String? objective;

  void setBasics({
    required String newName,
    required String newPlayerName,
    required int newNex,
    String? newAvatarUrl,
  }) {
    name = newName;
    playerName = newPlayerName;
    nex = newNex;
    avatarUrl = (newAvatarUrl == null || newAvatarUrl.trim().isEmpty)
        ? null
        : newAvatarUrl.trim();
    notifyListeners();
  }

  void setAttribute(String key, int value) {
    switch (key) {
      case 'AGI':
        agilidade = value;
        break;
      case 'INT':
        intelecto = value;
        break;
      case 'VIG':
        vigor = value;
        break;
      case 'PRE':
        presenca = value;
        break;
      case 'FOR':
        forca = value;
        break;
    }
    notifyListeners();
  }

  void chooseOrigin(CharacterOrigin origin) {
    selectedOrigin = origin;
    notifyListeners();
  }

  void chooseClass(CharacterClass characterClass) {
    selectedClass = characterClass;
    notifyListeners();
  }

  void setDetails({
    String? newGender,
    int? newAge,
    String? newAppearance,
    String? newPersonality,
    String? newBackground,
    String? newObjective,
  }) {
    gender = (newGender == null || newGender.trim().isEmpty)
        ? null
        : newGender.trim();
    age = newAge;
    appearance = (newAppearance == null || newAppearance.trim().isEmpty)
        ? null
        : newAppearance.trim();
    personality = (newPersonality == null || newPersonality.trim().isEmpty)
        ? null
        : newPersonality.trim();
    background = (newBackground == null || newBackground.trim().isEmpty)
        ? null
        : newBackground.trim();
    objective = (newObjective == null || newObjective.trim().isEmpty)
        ? null
        : newObjective.trim();
    notifyListeners();
  }

  bool validateBasics() =>
      name.trim().isNotEmpty &&
      playerName.trim().isNotEmpty &&
      nex >= 5 &&
      nex <= 100;
  bool validateAttributes() =>
      pointsAvailable >= 0 &&
      agilidade >= 0 &&
      intelecto >= 0 &&
      vigor >= 0 &&
      presenca >= 0 &&
      forca >= 0 &&
      agilidade <= 3 &&
      intelecto <= 3 &&
      vigor <= 3 &&
      presenca <= 3 &&
      forca <= 3;
  bool validateOrigin() => selectedOrigin != null;
  bool validateClass() => selectedClass != null;

  Character buildCharacter() {
    return Character(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name,
      playerName: playerName,
      origin: selectedOrigin?.name ?? '',
      characterClass: selectedClass?.name ?? '',
      nex: nex,
      avatarUrl: avatarUrl,
      skilledIn: skilledIn,
      attributes: CharacterAttributes(
        agilidade: agilidade,
        intelecto: intelecto,
        vigor: vigor,
        presenca: presenca,
        forca: forca,
      ),
      details: CharacterDetails(
        gender: gender,
        age: age,
        appearance: appearance,
        personality: personality,
        background: background,
        objective: objective,
      ),
    );
  }

  Future<Character> submit() async {
    // Criar personagem vinculado ao usuário autenticado
    final created = await _service.createUserCharacter(
      name: name,
      age: age ?? 0,
      skilledIn: skilledIn,
      playerName: playerName,
      origin: selectedOrigin?.name,
      characterClass: selectedClass?.name,
      nex: nex,
      avatarUrl: avatarUrl,
      agilidade: agilidade,
      intelecto: intelecto,
      vigor: vigor,
      presenca: presenca,
      forca: forca,
      gender: gender,
      appearance: appearance,
      personality: personality,
      background: background,
      objective: objective,
    );
    return created;
  }
}
