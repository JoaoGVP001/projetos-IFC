import 'package:flutter/foundation.dart';
import 'package:sigilrpg/services/auth_service.dart';

class AuthController extends ChangeNotifier {
  AuthController({AuthService? service}) : _service = service ?? AuthService();

  final AuthService _service;

  String? _token;
  Map<String, dynamic>? _user;
  bool _loading = false;
  String? _error;

  String? get token => _token;
  Map<String, dynamic>? get user => _user;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;
  bool get loading => _loading;
  String? get error => _error;

  Future<void> login(String email, String password) async {
    _setLoading(true);
    try {
      _error = null;
      final token = await _service.login(email, password);
      _token = token;
      _user = await _service.getCurrentUser();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> register(String name, String email, String password) async {
    _setLoading(true);
    try {
      _error = null;
      final result = await _service.register(name, email, password);
      _token = result['token'] as String?;
      _user = result['user'] as Map<String, dynamic>?;
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _setLoading(false);
    }
  }

  Future<void> logout() async {
    _setLoading(true);
    try {
      await _service.logout();
    } finally {
      _token = null;
      _user = null;
      _error = null;
      _setLoading(false);
      notifyListeners();
    }
  }

  void _setLoading(bool value) {
    _loading = value;
    notifyListeners();
  }
}
