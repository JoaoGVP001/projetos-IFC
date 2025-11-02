import 'package:sigilrpg/models/skill.dart';
import 'package:sigilrpg/utils/api.dart';

class SkillsService {
  SkillsService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Lista todas as habilidades de um personagem
  Future<List<Skill>> getSkills(String characterId) async {
    final response = await _client.getJson('/api/me/$characterId/skills');
    final dataList = response['data'] as List?;
    if (dataList == null) return [];
    return dataList.map((e) => Skill.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Obter habilidade específica por ID
  Future<Skill> getSkill(String characterId, String skillId) async {
    final response = await _client.getJson('/api/me/$characterId/skills/$skillId');
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados da habilidade não encontrados');
    }
    return Skill.fromJson(data);
  }

  /// Criar nova habilidade
  Future<Skill> createSkill(String characterId, Skill skill) async {
    final response = await _client.postJson(
      '/api/me/$characterId/skills',
      body: skill.toJson(),
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados da habilidade não encontrados');
    }
    return Skill.fromJson(data);
  }

  /// Atualizar habilidade
  Future<Skill> updateSkill(String characterId, String skillId, Map<String, dynamic> updates) async {
    final response = await _client.patchJson(
      '/api/me/$characterId/skills/$skillId',
      body: updates,
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados da habilidade não encontrados');
    }
    return Skill.fromJson(data);
  }

  /// Deletar habilidade
  Future<void> deleteSkill(String characterId, String skillId) async {
    await _client.deleteJson('/api/me/$characterId/skills/$skillId');
  }
}

