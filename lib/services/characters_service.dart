import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/utils/api.dart';

class CharactersService {
  CharactersService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  Future<List<Character>> fetchCharacters() async {
    final data = await _client.getJsonList('/api/v1/characters');
    return data.map((e) => _fromJson(e as Map<String, dynamic>)).toList();
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
    );
  }
}
