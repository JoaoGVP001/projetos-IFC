import 'package:sigilrpg/models/item.dart';
import 'package:sigilrpg/utils/api.dart';

class ItemsService {
  ItemsService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Lista todos os itens de um personagem
  Future<List<Item>> getItems(String characterId) async {
    final response = await _client.getJson('/api/me/$characterId/items');
    final dataList = response['data'] as List?;
    if (dataList == null) return [];
    return dataList.map((e) => Item.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Obter item específico por ID
  Future<Item> getItem(String characterId, String itemId) async {
    final response = await _client.getJson('/api/me/$characterId/items/$itemId');
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do item não encontrados');
    }
    return Item.fromJson(data);
  }

  /// Criar novo item
  Future<Item> createItem(String characterId, Item item) async {
    final response = await _client.postJson(
      '/api/me/$characterId/items',
      body: item.toJson(),
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do item não encontrados');
    }
    return Item.fromJson(data);
  }

  /// Atualizar item
  Future<Item> updateItem(String characterId, String itemId, Map<String, dynamic> updates) async {
    final response = await _client.patchJson(
      '/api/me/$characterId/items/$itemId',
      body: updates,
    );
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do item não encontrados');
    }
    return Item.fromJson(data);
  }

  /// Deletar item
  Future<void> deleteItem(String characterId, String itemId) async {
    await _client.deleteJson('/api/me/$characterId/items/$itemId');
  }
}

