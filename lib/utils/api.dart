import 'dart:async';
import 'dart:convert';
import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:http/http.dart' as http;

String resolveBaseUrl() {
  if (kIsWeb) return 'http://localhost:8000';
  try {
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
  } catch (_) {}
  return 'http://localhost:8000';
}

class ApiClient {
  ApiClient({String? baseUrl, http.Client? httpClient, Duration? timeout})
    : _baseUrl = baseUrl ?? resolveBaseUrl(),
      _client = httpClient ?? http.Client(),
      _timeout = timeout ?? const Duration(seconds: 60);

  final String _baseUrl;
  final http.Client _client;
  final Duration _timeout;
  String? _bearerToken;
  static String? _globalBearerToken;

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    return Uri.parse('$_baseUrl$path').replace(queryParameters: query);
  }

  Future<Map<String, dynamic>> getJson(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    final res = await _client
        .get(_uri(path, query), headers: _headers())
        .timeout(_timeout);
    _ensureSuccess(res);
    return _decode(res.body) as Map<String, dynamic>;
  }

  Future<List<dynamic>> getJsonList(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    final res = await _client
        .get(_uri(path, query), headers: _headers())
        .timeout(_timeout);
    _ensureSuccess(res);
    final decoded = _decode(res.body);
    // A API pode retornar um array diretamente ou um objeto com 'data'
    if (decoded is List) {
      return decoded;
    } else if (decoded is Map<String, dynamic>) {
      final data = decoded['data'];
      if (data is List) {
        return data;
      }
    }
    throw FormatException(
      'Expected array or object with data array, got: $decoded',
    );
  }

  Future<Map<String, dynamic>> postJson(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? query,
  }) async {
    final res = await _client
        .post(
          _uri(path, query),
          headers: _headers(contentType: true),
          body: body != null ? json.encode(body) : null,
        )
        .timeout(_timeout);
    _ensureSuccess(res);
    return _decode(res.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> patchJson(
    String path, {
    Map<String, dynamic>? body,
    Map<String, dynamic>? query,
  }) async {
    final res = await _client
        .patch(
          _uri(path, query),
          headers: _headers(contentType: true),
          body: body != null ? json.encode(body) : null,
        )
        .timeout(_timeout);
    _ensureSuccess(res);
    return _decode(res.body) as Map<String, dynamic>;
  }

  Future<void> delete(String path) async {
    final res = await _client
        .delete(_uri(path), headers: _headers())
        .timeout(_timeout);
    _ensureSuccess(res);
  }

  Future<Map<String, dynamic>> deleteJson(String path) async {
    final res = await _client
        .delete(_uri(path), headers: _headers())
        .timeout(_timeout);
    _ensureSuccess(res);
    try {
      return _decode(res.body) as Map<String, dynamic>;
    } catch (_) {
      return {'message': 'deleted'};
    }
  }

  void setBearerToken(String? token) {
    _bearerToken = token;
  }

  static void setGlobalBearerToken(String? token) {
    _globalBearerToken = token;
  }

  Map<String, String> _headers({bool contentType = false}) {
    final headers = <String, String>{};
    if (contentType) headers['Content-Type'] = 'application/json';
    final token = _bearerToken ?? _globalBearerToken;
    if (token != null && token.isNotEmpty)
      headers['Authorization'] = 'Bearer $token';
    return headers;
  }

  void _ensureSuccess(http.Response res) {
    if (res.statusCode < 200 || res.statusCode >= 300) {
      // Tentar extrair mensagem de erro da resposta da API
      String errorMessage = 'HTTP ${res.statusCode}';
      try {
        final jsonBody = json.decode(res.body);
        if (jsonBody is Map<String, dynamic>) {
          final message = jsonBody['message'] as String?;
          final error = jsonBody['error'] as String?;
          final errorDetail = jsonBody['error_detail'] as String?;
          if (errorDetail != null) {
            errorMessage = errorDetail;
          } else if (error != null) {
            errorMessage = error;
          } else if (message != null) {
            errorMessage = message;
          }
          // Incluir erros de validação se existirem
          final errors = jsonBody['errors'] as Map<String, dynamic>?;
          if (errors != null && errors.isNotEmpty) {
            final errorList = errors.values
                .expand((e) => (e as List<dynamic>).map((e) => e.toString()))
                .join(', ');
            errorMessage = '$errorMessage: $errorList';
          }
        }
      } catch (_) {
        // Se não conseguir parsear, usar o body completo
        errorMessage = 'HTTP ${res.statusCode}: ${res.body}';
      }
      throw HttpException(errorMessage);
    }
  }

  String get baseUrl => _baseUrl;

  Future<bool> testConnection() async {
    try {
      // Testar conexão com o endpoint raiz da API
      final res = await _client
          .get(_uri('/'), headers: _headers())
          .timeout(const Duration(seconds: 10));
      return res.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  dynamic _decode(String body) {
    try {
      return json.decode(body);
    } catch (e) {
      throw FormatException('Invalid JSON: $e');
    }
  }
}

class HttpException implements Exception {
  final String message;
  HttpException(this.message);
  @override
  String toString() => 'HttpException($message)';
}
