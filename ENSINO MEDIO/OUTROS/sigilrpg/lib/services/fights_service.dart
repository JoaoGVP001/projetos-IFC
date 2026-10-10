import 'package:sigilrpg/utils/api.dart';

class Fight {
  final int id;
  final int opponentId;
  final int characterId;
  final String status; // 'won', 'lost', 'draw'
  final int experience;
  final String? createdAt;
  final String? updatedAt;

  Fight({
    required this.id,
    required this.opponentId,
    required this.characterId,
    required this.status,
    required this.experience,
    this.createdAt,
    this.updatedAt,
  });

  factory Fight.fromJson(Map<String, dynamic> json) {
    return Fight(
      id: (json['id'] as num).toInt(),
      opponentId: (json['opponent_id'] as num).toInt(),
      characterId: (json['character_id'] as num).toInt(),
      status: json['status'] as String,
      experience: (json['experience'] as num).toInt(),
      createdAt: json['created_at'] as String?,
      updatedAt: json['updated_at'] as String?,
    );
  }
}

class FightsService {
  FightsService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Lista todas as lutas do personagem do usuário autenticado
  Future<List<Fight>> getUserFights() async {
    // A API retorna: {'message': 'fights_list', 'data': [...]}
    final response = await _client.getJson('/api/me/fights/');
    final data = response['data'] as List<dynamic>?;
    if (data == null) {
      throw Exception('Dados de lutas não encontrados');
    }
    return data.map((e) => Fight.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Criar uma nova luta para o personagem do usuário
  Future<Fight> createFight(int opponentId) async {
    // A API retorna: {'message': 'fight_completed', 'data': {...}}
    final response = await _client.postJson(
      '/api/me/fights/',
      body: {'opponent_id': opponentId},
    );

    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados da luta não encontrados');
    }

    return Fight.fromJson(data);
  }
}
