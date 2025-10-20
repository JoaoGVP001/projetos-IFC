import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/utils/api.dart';

class CharactersService {
  CharactersService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  Future<List<Character>> fetchCharacters() async {
    final data = await _client.getJsonList('/api/v1/characters');
    return data.map((e) => _fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Character> fetchCharacter(String id) async {
    final data = await _client.getJson('/api/v1/characters/$id');
    return _fromJson(data);
  }

  Future<Character> createCharacter(Character character) async {
    final data = await _client.postJson(
      '/api/v1/characters',
      body: _toJson(character),
    );
    return _fromJson(data);
  }

  Future<Character> updateCharacter(
    String id,
    Map<String, dynamic> updates,
  ) async {
    final data = await _client.patchJson(
      '/api/v1/characters/$id',
      body: updates,
    );
    return _fromJson(data);
  }

  Map<String, dynamic> _toJson(Character character) {
    return {
      'name': character.name,
      'playerName': character.playerName,
      'origin': character.origin,
      'characterClass': character.characterClass,
      'nex': character.nex,
      'avatarUrl': character.avatarUrl,
      'agilidade': character.attributes.agilidade,
      'intelecto': character.attributes.intelecto,
      'vigor': character.attributes.vigor,
      'presenca': character.attributes.presenca,
      'forca': character.attributes.forca,
      'gender': character.details.gender,
      'age': character.details.age,
      'appearance': character.details.appearance,
      'personality': character.details.personality,
      'background': character.details.background,
      'objective': character.details.objective,
    };
  }

  Character _fromJson(Map<String, dynamic> json) {
    return Character(
      id: json['id'].toString(),
      name: json['name'] as String? ?? '',
      playerName: json['playerName'] as String? ?? '',
      origin: json['origin'] as String? ?? '',
      characterClass: json['characterClass'] as String? ?? '',
      nex: (json['nex'] as num?)?.toInt() ?? 0,
      avatarUrl: json['avatarUrl'] as String?,
      attributes: CharacterAttributes(
        agilidade: (json['agilidade'] as num?)?.toInt() ?? 1,
        intelecto: (json['intelecto'] as num?)?.toInt() ?? 1,
        vigor: (json['vigor'] as num?)?.toInt() ?? 1,
        presenca: (json['presenca'] as num?)?.toInt() ?? 1,
        forca: (json['forca'] as num?)?.toInt() ?? 1,
      ),
      details: CharacterDetails(
        gender: json['gender'] as String?,
        age: (json['age'] as num?)?.toInt(),
        appearance: json['appearance'] as String?,
        personality: json['personality'] as String?,
        background: json['background'] as String?,
        objective: json['objective'] as String?,
      ),
    );
  }
}
