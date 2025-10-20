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
    return _decode(res.body) as List<dynamic>;
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
      throw HttpException('HTTP ${res.statusCode}: ${res.body}');
    }
  }

  String get baseUrl => _baseUrl;

  Future<bool> testConnection() async {
    try {
      final res = await _client
          .get(_uri('/docs'), headers: _headers())
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
