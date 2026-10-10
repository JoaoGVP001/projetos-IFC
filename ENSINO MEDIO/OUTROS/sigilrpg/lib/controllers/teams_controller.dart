import 'package:flutter/foundation.dart';
import 'package:sigilrpg/models/team.dart';
import 'package:sigilrpg/services/campaigns_service.dart';

class TeamsController extends ChangeNotifier {
  TeamsController({CampaignsService? service})
    : _service = service ?? CampaignsService();

  final CampaignsService _service;
  final List<Team> _teams = <Team>[];
  bool _isLoading = false;
  String? _error;

  List<Team> get teams => List.unmodifiable(_teams);
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> load() async {
    _setLoading(true);
    _clearError();

    try {
      // Carregar todas as campanhas
      final campaigns = await _service.fetchCampaigns();

      final List<Team> loadedTeams = <Team>[];
      for (final campaign in campaigns) {
        final teams = await _service.fetchCampaignParties(
          campaign.id,
          campaignName: campaign.name,
        );
        loadedTeams.addAll(teams);
      }

      _teams
        ..clear()
        ..addAll(loadedTeams);
      notifyListeners();
    } catch (e) {
      _setError('Erro ao carregar equipes: $e');
    } finally {
      _setLoading(false);
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String message) {
    _error = message;
    notifyListeners();
  }

  void _clearError() {
    _error = null;
  }
}
