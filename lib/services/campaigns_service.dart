import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/utils/api.dart';

class CampaignsService {
  CampaignsService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  Future<List<Campaign>> fetchCampaigns() async {
    final data = await _client.getJsonList('/api/v1/campaigns');
    return data
        .map((e) => Campaign.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Campaign> fetchCampaign(String id) async {
    final data = await _client.getJson('/api/v1/campaigns/$id');
    return Campaign.fromJson(data);
  }

  Future<Campaign> createCampaign(Campaign campaign) async {
    final data = await _client.postJson(
      '/api/v1/campaigns',
      body: _toJson(campaign),
    );
    return Campaign.fromJson(data);
  }

  Future<Campaign> updateCampaign(
    String id,
    Map<String, dynamic> updates,
  ) async {
    final data = await _client.patchJson(
      '/api/v1/campaigns/$id',
      body: updates,
    );
    return Campaign.fromJson(data);
  }

  Future<void> deleteCampaign(String id) async {
    await _client.delete('/api/v1/campaigns/$id');
  }

  Map<String, dynamic> _toJson(Campaign campaign) {
    return {
      'name': campaign.name,
      'description': campaign.description,
      'system': campaign.system,
      'max_players': campaign.maxPlayers,
      'is_active': campaign.isActive,
      'is_public': campaign.isPublic,
      'setting': campaign.setting,
      'rules': campaign.rules,
      'notes': campaign.notes,
      'master_name': campaign.masterName,
    };
  }
}
