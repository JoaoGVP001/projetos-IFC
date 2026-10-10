import 'package:sigilrpg/models/ritual.dart';
import 'package:sigilrpg/utils/api.dart';

class RitualsService {
  RitualsService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Lista todos os rituais de um personagem
  Future<List<Ritual>> getRituals(String characterId) async {
    final response = await _client.getJson('/api/me/$characterId/rituals');
    final dataList = response['data'] as List?;
    if (dataList == null) return [];
    return dataList.map((e) => Ritual.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Obter ritual específico por ID
  Future<Ritual> getRitual(String characterId, String ritualId) async {
    final response = await _client.getJson('/api/me/$characterId/rituals/$ritualId');
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do ritual não encontrados');
    }
    return Ritual.fromJson(data);
  }

  /// Criar novo ritual
  Future<Ritual> createRitual(String characterId, Ritual ritual) async {
    final response = await _client.postJson(
      '/api/me/$characterId/rituals',
      body: ritual.toJson(),
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do ritual não encontrados');
    }
    return Ritual.fromJson(data);
  }

  /// Atualizar ritual
  Future<Ritual> updateRitual(String characterId, String ritualId, Map<String, dynamic> updates) async {
    final response = await _client.patchJson(
      '/api/me/$characterId/rituals/$ritualId',
      body: updates,
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do ritual não encontrados');
    }
    return Ritual.fromJson(data);
  }

  /// Deletar ritual
  Future<void> deleteRitual(String characterId, String ritualId) async {
    await _client.deleteJson('/api/me/$characterId/rituals/$ritualId');
  }
}

