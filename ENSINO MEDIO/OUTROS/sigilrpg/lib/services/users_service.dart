import 'package:sigilrpg/utils/api.dart';

class UsersService {
  UsersService({ApiClient? client}) : _client = client ?? ApiClient();
  final ApiClient _client;

  Future<List<Map<String, dynamic>>> listUsers() async {
    final response = await _client.getJson('/api/users');
    final data = response['data'] as List?;
    if (data == null) return [];
    return data.cast<Map<String, dynamic>>();
  }
}


