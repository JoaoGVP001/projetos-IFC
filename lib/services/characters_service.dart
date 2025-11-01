import 'package:sigilrpg/models/character.dart';
import 'package:sigilrpg/utils/api.dart';

class CharactersService {
  CharactersService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Lista todos os personagens do sistema (públicos)
  Future<List<Character>> fetchCharacters() async {
    // A API retorna um array diretamente
    final data = await _client.getJsonList('/api/characters/');
    return data.map((e) => _fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Obter personagem específico por ID
  Future<Character> fetchCharacter(String id) async {
    // A API retorna o objeto diretamente
    final data = await _client.getJson('/api/characters/$id');
    return _fromJson(data);
  }

  /// Criar novo personagem (sistema)
  Future<Character> createCharacter(Character character) async {
    final data = await _client.postJson(
      '/api/characters/',
      body: _toJson(character),
    );
    return _fromJson(data);
  }

  /// Atualizar personagem (sistema)
  Future<Character> updateCharacter(
    String id,
    Map<String, dynamic> updates,
  ) async {
    final data = await _client.patchJson('/api/characters/$id', body: updates);
    return _fromJson(data);
  }

  /// Listar todos os personagens do usuário autenticado
  Future<List<Character>> getUserCharacters() async {
    try {
      // A API retorna: {'message': 'characters', 'data': [...]}
      final response = await _client.getJson('/api/me/');
      final dataList = response['data'];
      
      // Se data for uma lista, usar diretamente
      if (dataList is List) {
        return dataList.map((e) => _fromJson(e as Map<String, dynamic>)).toList();
      }
      
      // Se data for null ou não for lista, retornar lista vazia (usuário sem personagens)
      return [];
    } catch (e) {
      // Se houver erro (ex: 400 quando não há personagens), retornar lista vazia
      // Isso evita quebrar o login quando usuário ainda não tem personagens
      return [];
    }
  }

  /// Obter personagem específico do usuário autenticado
  Future<Character> getUserCharacter(String characterId) async {
    // A API retorna: {'message': 'character', 'data': {...}}
    final response = await _client.getJson('/api/me/$characterId');
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do personagem não encontrados');
    }
    return _fromJson(data);
  }

  /// Atualizar personagem do usuário autenticado
  Future<Character> updateUserCharacter(
    String characterId,
    Map<String, dynamic> updates,
  ) async {
    final response = await _client.patchJson(
      '/api/me/$characterId',
      body: updates,
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do personagem não encontrados');
    }
    return _fromJson(data);
  }

  /// Deletar personagem do usuário autenticado
  Future<void> deleteUserCharacter(String characterId) async {
    await _client.deleteJson('/api/me/$characterId');
  }

  /// Criar personagem para o usuário autenticado
  Future<Character> createUserCharacter({
    required String name,
    required int age,
    required String skilledIn,
    String? playerName,
    String? origin,
    String? characterClass,
    int? nex,
    String? avatarUrl,
    int? agilidade,
    int? intelecto,
    int? vigor,
    int? presenca,
    int? forca,
    String? gender,
    String? appearance,
    String? personality,
    String? background,
    String? objective,
  }) async {
    final body = <String, dynamic>{
      'name': name,
      'age': age,
      'skilled_in': skilledIn,
    };

    if (playerName != null) body['player_name'] = playerName;
    if (origin != null) body['origin'] = origin;
    if (characterClass != null) body['character_class'] = characterClass;
    if (nex != null) body['nex'] = nex;
    if (avatarUrl != null) body['avatar_url'] = avatarUrl;
    if (agilidade != null) body['agilidade'] = agilidade;
    if (intelecto != null) body['intelecto'] = intelecto;
    if (vigor != null) body['vigor'] = vigor;
    if (presenca != null) body['presenca'] = presenca;
    if (forca != null) body['forca'] = forca;
    if (gender != null) body['gender'] = gender;
    if (appearance != null) body['appearance'] = appearance;
    if (personality != null) body['personality'] = personality;
    if (background != null) body['background'] = background;
    if (objective != null) body['objective'] = objective;

    // A API retorna: {'message': 'character_created', 'data': {...}}
    final response = await _client.postJson('/api/me/', body: body);
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do personagem não encontrados');
    }
    return _fromJson(data);
  }

  Map<String, dynamic> _toJson(Character character) {
    return {
      'name': character.name,
      'player_name': character.playerName,
      'origin': character.origin,
      'character_class': character.characterClass,
      'nex': character.nex,
      'avatar_url': character.avatarUrl,
      'skilled_in': character.skilledIn,
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
      playerName: json['player_name'] as String? ?? '',
      origin: json['origin'] as String? ?? '',
      characterClass: json['character_class'] as String? ?? '',
      nex: (json['nex'] as num?)?.toInt() ?? 0,
      avatarUrl: json['avatar_url'] as String?,
      skilledIn: json['skilled_in'] as String? ?? 'Combat',
      userId: (json['user_id'] as num?)?.toInt(),
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
