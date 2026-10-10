import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/models/campaign_member.dart';
import 'package:sigilrpg/models/team.dart';
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

  Future<List<CampaignMember>> fetchCampaignMembers(String campaignId) async {
    final data = await _client.getJsonList('/api/v1/campaigns/$campaignId/characters');
    return data
        .map((e) => CampaignMember.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<CampaignMember> addCampaignMember(
    String campaignId,
    Map<String, dynamic> body,
  ) async {
    final data = await _client.postJson(
      '/api/v1/campaigns/$campaignId/characters',
      body: body,
    );
    return CampaignMember.fromJson(data);
  }

  Future<CampaignMember> updateCampaignMember(
    String campaignId,
    String characterId,
    Map<String, dynamic> body,
  ) async {
    final data = await _client.patchJson(
      '/api/v1/campaigns/$campaignId/characters/$characterId',
      body: body,
    );
    return CampaignMember.fromJson(data);
  }

  Future<void> removeCampaignMember(String campaignId, String characterId) async {
    await _client.delete('/api/v1/campaigns/$campaignId/characters/$characterId');
  }

  Future<List<Team>> fetchCampaignParties(String campaignId, {String? campaignName}) async {
    final data = await _client.getJsonList('/api/v1/campaigns/$campaignId/parties');
    return data
        .map(
          (e) => Team.fromJson(
            e as Map<String, dynamic>,
            campaignName: campaignName,
          ),
        )
        .toList();
  }

  Future<Team> createParty(
    String campaignId,
    Map<String, dynamic> body, {
    String? campaignName,
  }) async {
    final data = await _client.postJson(
      '/api/v1/campaigns/$campaignId/parties',
      body: body,
    );
    return Team.fromJson(data, campaignName: campaignName);
  }

  Future<Team> updateParty(
    String campaignId,
    String partyId,
    Map<String, dynamic> body, {
    String? campaignName,
  }) async {
    final data = await _client.patchJson(
      '/api/v1/campaigns/$campaignId/parties/$partyId',
      body: body,
    );
    return Team.fromJson(data, campaignName: campaignName);
  }

  Future<void> deleteParty(String campaignId, String partyId) async {
    await _client.delete('/api/v1/campaigns/$campaignId/parties/$partyId');
  }

  Future<TeamMember> addPartyMember(
    String campaignId,
    String partyId,
    Map<String, dynamic> body,
  ) async {
    final data = await _client.postJson(
      '/api/v1/campaigns/$campaignId/parties/$partyId/members',
      body: body,
    );
    return TeamMember.fromJson(data);
  }

  Future<TeamMember> updatePartyMember(
    String campaignId,
    String partyId,
    String characterId,
    Map<String, dynamic> body,
  ) async {
    final data = await _client.patchJson(
      '/api/v1/campaigns/$campaignId/parties/$partyId/members/$characterId',
      body: body,
    );
    return TeamMember.fromJson(data);
  }

  Future<void> removePartyMember(
    String campaignId,
    String partyId,
    String characterId,
  ) async {
    await _client.delete(
      '/api/v1/campaigns/$campaignId/parties/$partyId/members/$characterId',
    );
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
