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
      _timeout = timeout ?? const Duration(seconds: 15);

  final String _baseUrl;
  final http.Client _client;
  final Duration _timeout;

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    return Uri.parse('$_baseUrl$path').replace(queryParameters: query);
  }

  Future<Map<String, dynamic>> getJson(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    final res = await _client.get(_uri(path, query)).timeout(_timeout);
    _ensureSuccess(res);
    return _decode(res.body) as Map<String, dynamic>;
  }

  Future<List<dynamic>> getJsonList(
    String path, {
    Map<String, dynamic>? query,
  }) async {
    final res = await _client.get(_uri(path, query)).timeout(_timeout);
    _ensureSuccess(res);
    return _decode(res.body) as List<dynamic>;
  }

  void _ensureSuccess(http.Response res) {
    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw HttpException('HTTP ${res.statusCode}: ${res.body}');
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
