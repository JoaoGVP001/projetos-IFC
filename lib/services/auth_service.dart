import 'package:sigilrpg/utils/api.dart';

class AuthService {
  AuthService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  String get baseUrl => _client.baseUrl;

  Future<bool> testConnection() async {
    return await _client.testConnection();
  }

  Future<Map<String, dynamic>> register({
    required String username,
    required String email,
    required String password,
    String? fullName,
  }) async {
    final data = await _client.postJson(
      '/api/v1/auth/register',
      body: {
        'username': username,
        'email': email,
        'password': password,
        if (fullName != null) 'full_name': fullName,
      },
    );
    return data;
  }

  Future<String> login({
    required String username,
    required String password,
  }) async {
    final data = await _client.postJson(
      '/api/v1/auth/login',
      body: {'username': username, 'password': password},
    );
    final token = (data['access_token'] as String?) ?? '';
    _client.setBearerToken(token);
    return token;
  }

  void setToken(String? token) {
    _client.setBearerToken(token);
  }
}
