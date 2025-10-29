import 'package:sigilrpg/utils/api.dart';

class AuthService {
  AuthService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  /// Login de usuário
  /// Retorna o token JWT
  Future<String> login(String email, String password) async {
    final response = await _client.postJson(
      '/api/auth/login',
      body: {'email': email, 'password': password},
    );

    // A API retorna: {'message': 'token_generated', 'data': {'token': '...'}}
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null || data['token'] == null) {
      throw Exception('Token não encontrado na resposta');
    }

    final token = data['token'] as String;
    // Configurar o token global
    ApiClient.setGlobalBearerToken(token);
    _client.setBearerToken(token);

    return token;
  }

  /// Registro de novo usuário
  /// Retorna o token JWT
  Future<Map<String, dynamic>> register(
    String name,
    String email,
    String password,
  ) async {
    final response = await _client.postJson(
      '/api/auth/register',
      body: {'name': name, 'email': email, 'password': password},
    );

    // A API retorna: {'message': 'user_created', 'data': {'user': {...}, 'token': '...'}}
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados não encontrados na resposta');
    }

    final token = data['token'] as String;
    final user = data['user'] as Map<String, dynamic>;

    // Configurar o token global
    ApiClient.setGlobalBearerToken(token);
    _client.setBearerToken(token);

    return {'token': token, 'user': user};
  }

  /// Obter usuário autenticado
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _client.getJson('/api/auth/user');

    // A API retorna: {'message': 'authenticated_user', 'data': {...}}
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null) {
      throw Exception('Dados do usuário não encontrados');
    }

    return data;
  }

  /// Atualizar token JWT
  Future<String> refreshToken() async {
    final response = await _client.patchJson('/api/auth/');

    // A API retorna: {'message': 'token_refreshed', 'data': {'token': '...'}}
    final data = response['data'] as Map<String, dynamic>?;
    if (data == null || data['token'] == null) {
      throw Exception('Token não encontrado na resposta');
    }

    final token = data['token'] as String;
    ApiClient.setGlobalBearerToken(token);
    _client.setBearerToken(token);

    return token;
  }

  /// Logout (invalidar token)
  Future<void> logout() async {
    try {
      await _client.delete('/api/auth/');
    } finally {
      // Sempre limpar o token local, mesmo se a requisição falhar
      ApiClient.setGlobalBearerToken(null);
      _client.setBearerToken(null);
    }
  }

  /// Definir token para requisições
  void setToken(String? token) {
    ApiClient.setGlobalBearerToken(token);
    _client.setBearerToken(token);
  }
}
