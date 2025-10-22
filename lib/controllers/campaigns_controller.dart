import 'package:flutter/foundation.dart';
import 'package:sigilrpg/models/campaign.dart';
import 'package:sigilrpg/services/campaigns_service.dart';

class CampaignsController extends ChangeNotifier {
  CampaignsController({CampaignsService? service})
    : _service = service ?? CampaignsService();

  final CampaignsService _service;
  final List<Campaign> _campaigns = <Campaign>[];
  bool _isLoading = false;
  String? _error;

  List<Campaign> get campaigns => List.unmodifiable(_campaigns);
  bool get isLoading => _isLoading;
  String? get error => _error;

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
    notifyListeners();
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
