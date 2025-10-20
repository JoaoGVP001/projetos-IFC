import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sigilrpg/services/auth_service.dart';
import 'package:sigilrpg/utils/api.dart';

class AuthController extends ChangeNotifier {
  AuthController({AuthService? service}) : _service = service ?? AuthService();

  final AuthService _service;
  String? _token;
  String? _username;
  bool _loading = false;

  String? get token => _token;
  String? get username => _username;
  bool get isAuthenticated => _token != null && _token!.isNotEmpty;
  bool get isLoading => _loading;

  Future<void> loadSession() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
    _username = prefs.getString('auth_username');
    ApiClient.setGlobalBearerToken(_token);
    notifyListeners();
  }

  Future<void> login(String username, String password) async {
    _loading = true;
    notifyListeners();
    try {
      final token = await _service.login(
        username: username,
        password: password,
      );
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', token);
      await prefs.setString('auth_username', username);
      _token = token;
      _username = username;
      ApiClient.setGlobalBearerToken(token);
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> register({
    required String username,
    required String email,
    required String password,
    String? fullName,
  }) async {
    _loading = true;
    notifyListeners();
    try {
      await _service.register(
        username: username,
        email: email,
        password: password,
        fullName: fullName,
      );
      await login(username, password);
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('auth_username');
    _token = null;
    _username = null;
    ApiClient.setGlobalBearerToken(null);
    notifyListeners();
  }
}
