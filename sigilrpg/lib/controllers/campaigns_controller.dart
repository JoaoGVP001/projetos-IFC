import 'package:flutter/foundation.dart';
import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/models/campaign_member.dart';
import 'package:sigilrpg/models/team.dart';
import 'package:sigilrpg/services/campaigns_service.dart';

class CampaignsController extends ChangeNotifier {
  CampaignsController({CampaignsService? service})
    : _service = service ?? CampaignsService();

  final CampaignsService _service;
  final List<Campaign> _campaigns = <Campaign>[];
  bool _isLoading = false;
  String? _error;
  final Map<String, List<CampaignMember>> _membersByCampaign =
      <String, List<CampaignMember>>{};
  final Map<String, List<Team>> _teamsByCampaign =
      <String, List<Team>>{};
  final Set<String> _loadingMembers = <String>{};
  final Set<String> _loadingTeams = <String>{};
  final Map<String, String?> _membersErrors = <String, String?>{};
  final Map<String, String?> _teamsErrors = <String, String?>{};

  List<Campaign> get campaigns => List.unmodifiable(_campaigns);
  bool get isLoading => _isLoading;
  String? get error => _error;
  List<CampaignMember> membersFor(String campaignId) =>
      List.unmodifiable(_membersByCampaign[campaignId] ?? const []);
  List<Team> teamsFor(String campaignId) =>
      List.unmodifiable(_teamsByCampaign[campaignId] ?? const []);
  bool membersLoading(String campaignId) =>
      _loadingMembers.contains(campaignId);
  bool teamsLoading(String campaignId) => _loadingTeams.contains(campaignId);
  String? membersError(String campaignId) => _membersErrors[campaignId];
  String? teamsError(String campaignId) => _teamsErrors[campaignId];

  Future<void> loadCampaigns() async {
    _setLoading(true);
    _clearError();

    try {
      final list = await _service.fetchCampaigns();
      _campaigns
        ..clear()
        ..addAll(list);
    } catch (e) {
      _setError('Erro ao carregar campanhas: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> createCampaign(Campaign campaign) async {
    _setLoading(true);
    _clearError();

    try {
      final createdCampaign = await _service.createCampaign(campaign);
      _campaigns.add(createdCampaign);
      notifyListeners();
    } catch (e) {
      _setError('Erro ao criar campanha: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> updateCampaign(String id, Map<String, dynamic> updates) async {
    _setLoading(true);
    _clearError();

    try {
      final updatedCampaign = await _service.updateCampaign(id, updates);
      final index = _campaigns.indexWhere((c) => c.id == id);
      if (index != -1) {
        _campaigns[index] = updatedCampaign;
        notifyListeners();
      }
    } catch (e) {
      _setError('Erro ao atualizar campanha: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> deleteCampaign(String id) async {
    _setLoading(true);
    _clearError();

    try {
      await _service.deleteCampaign(id);
      _campaigns.removeWhere((c) => c.id == id);
      _membersByCampaign.remove(id);
      _teamsByCampaign.remove(id);
      _membersErrors.remove(id);
      _teamsErrors.remove(id);
      notifyListeners();
    } catch (e) {
      _setError('Erro ao deletar campanha: $e');
    } finally {
      _setLoading(false);
    }
  }

  void add(Campaign campaign) {
    _campaigns.add(campaign);
    notifyListeners();
  }

  void removeById(String id) {
    _campaigns.removeWhere((c) => c.id == id);
    _membersByCampaign.remove(id);
    _teamsByCampaign.remove(id);
    notifyListeners();
  }

  Future<void> loadCampaignMembers(String campaignId) async {
    _loadingMembers.add(campaignId);
    _membersErrors.remove(campaignId);
    notifyListeners();

    try {
      final members = await _service.fetchCampaignMembers(campaignId);
      _membersByCampaign[campaignId] = members;
    } catch (e) {
      _membersErrors[campaignId] = 'Erro ao carregar membros: $e';
    } finally {
      _loadingMembers.remove(campaignId);
      notifyListeners();
    }
  }

  Future<void> addCharacterToCampaign({
    required String campaignId,
    required String characterId,
    String? role,
    bool? isActive,
    String? notes,
  }) async {
    final body = <String, dynamic>{'character_id': characterId};
    if (role != null) body['role'] = role;
    if (isActive != null) body['is_active'] = isActive;
    if (notes != null) body['notes'] = notes;

    final member = await _service.addCampaignMember(campaignId, body);
    final members = _membersByCampaign.putIfAbsent(
      campaignId,
      () => <CampaignMember>[],
    );
    members.add(member);
    notifyListeners();
  }

  Future<void> updateCampaignMember({
    required String campaignId,
    required String characterId,
    String? role,
    bool clearRole = false,
    bool? isActive,
    String? notes,
  }) async {
    final body = <String, dynamic>{};
    if (role != null) {
      body['role'] = role;
    } else if (clearRole) {
      body['role'] = null;
    }
    if (isActive != null) body['is_active'] = isActive;
    if (notes != null) body['notes'] = notes;

    final updated = await _service.updateCampaignMember(
      campaignId,
      characterId,
      body,
    );

    final members = _membersByCampaign[campaignId];
    if (members != null) {
      final index = members.indexWhere((m) => m.characterId == characterId);
      if (index != -1) {
        members[index] = updated;
        notifyListeners();
      }
    }
  }

  Future<void> removeCampaignMember({
    required String campaignId,
    required String characterId,
  }) async {
    await _service.removeCampaignMember(campaignId, characterId);
    final members = _membersByCampaign[campaignId];
    if (members != null) {
      members.removeWhere((m) => m.characterId == characterId);
      notifyListeners();
    }
  }

  Future<void> loadCampaignTeams(String campaignId, {String? campaignName}) async {
    _loadingTeams.add(campaignId);
    _teamsErrors.remove(campaignId);
    notifyListeners();

    try {
      final teams = await _service.fetchCampaignParties(
        campaignId,
        campaignName: campaignName,
      );
      _teamsByCampaign[campaignId] = teams;
    } catch (e) {
      _teamsErrors[campaignId] = 'Erro ao carregar equipes: $e';
    } finally {
      _loadingTeams.remove(campaignId);
      notifyListeners();
    }
  }

  Future<Team> createTeam({
    required String campaignId,
    required String name,
    String? description,
    String? campaignName,
  }) async {
    final payload = <String, dynamic>{'name': name};
    if (description != null) payload['description'] = description;

    final team = await _service.createParty(
      campaignId,
      payload,
      campaignName: campaignName,
    );

    final teams = _teamsByCampaign.putIfAbsent(
      campaignId,
      () => <Team>[],
    );
    teams.add(team);
    notifyListeners();
    return team;
  }

  Future<void> updateTeam({
    required String campaignId,
    required String teamId,
    String? name,
    String? description,
    String? campaignName,
  }) async {
    final payload = <String, dynamic>{};
    if (name != null) payload['name'] = name;
    if (description != null) payload['description'] = description;

    final updated = await _service.updateParty(
      campaignId,
      teamId,
      payload,
      campaignName: campaignName,
    );

    final teams = _teamsByCampaign[campaignId];
    if (teams != null) {
      final index = teams.indexWhere((team) => team.id == teamId);
      if (index != -1) {
        teams[index] = updated;
        notifyListeners();
      }
    }
  }

  Future<void> deleteTeam({
    required String campaignId,
    required String teamId,
  }) async {
    await _service.deleteParty(campaignId, teamId);
    final teams = _teamsByCampaign[campaignId];
    if (teams != null) {
      teams.removeWhere((team) => team.id == teamId);
      notifyListeners();
    }
  }

  Future<void> addMemberToTeam({
    required String campaignId,
    required String teamId,
    required String characterId,
    String? role,
  }) async {
    final payload = <String, dynamic>{'character_id': characterId};
    if (role != null) payload['role'] = role;

    final member = await _service.addPartyMember(
      campaignId,
      teamId,
      payload,
    );

    final teams = _teamsByCampaign[campaignId];
    if (teams != null) {
      final index = teams.indexWhere((team) => team.id == teamId);
      if (index != -1) {
        final members = List<TeamMember>.from(teams[index].members)..add(member);
        teams[index] = teams[index].copyWith(members: members);
        notifyListeners();
      }
    }
  }

  Future<void> updateTeamMember({
    required String campaignId,
    required String teamId,
    required String characterId,
    String? role,
    bool clearRole = false,
  }) async {
    final payload = <String, dynamic>{};
    if (role != null) {
      payload['role'] = role;
    } else if (clearRole) {
      payload['role'] = null;
    }

    final updated = await _service.updatePartyMember(
      campaignId,
      teamId,
      characterId,
      payload,
    );

    final teams = _teamsByCampaign[campaignId];
    if (teams != null) {
      final teamIndex = teams.indexWhere((team) => team.id == teamId);
      if (teamIndex != -1) {
        final members = List<TeamMember>.from(teams[teamIndex].members);
        final memberIndex =
            members.indexWhere((member) => member.characterId == characterId);
        if (memberIndex != -1) {
          members[memberIndex] = updated;
          teams[teamIndex] = teams[teamIndex].copyWith(members: members);
          notifyListeners();
        }
      }
    }
  }

  Future<void> removeTeamMember({
    required String campaignId,
    required String teamId,
    required String characterId,
  }) async {
    await _service.removePartyMember(campaignId, teamId, characterId);

    final teams = _teamsByCampaign[campaignId];
    if (teams != null) {
      final teamIndex = teams.indexWhere((team) => team.id == teamId);
      if (teamIndex != -1) {
        final members = List<TeamMember>.from(teams[teamIndex].members)
          ..removeWhere((member) => member.characterId == characterId);
        teams[teamIndex] = teams[teamIndex].copyWith(members: members);
        notifyListeners();
      }
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
  }
}
