import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import 'storage_service.dart';

class ApiService {
  final StorageService _storageService = StorageService();

  Future<Map<String, String>> _getHeaders() async {
    final token = await _storageService.getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<Map<String, dynamic>> get(String endpoint) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(
            Uri.parse('${ApiConfig.baseUrl}$endpoint'),
            headers: headers,
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .post(
            Uri.parse('${ApiConfig.baseUrl}$endpoint'),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> put(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .put(
            Uri.parse('${ApiConfig.baseUrl}$endpoint'),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> delete(String endpoint) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .delete(
            Uri.parse('${ApiConfig.baseUrl}$endpoint'),
            headers: headers,
          )
          .timeout(ApiConfig.timeout);

      return _handleResponse(response);
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) {
        return {'success': true};
      }
      return jsonDecode(response.body);
    } else {
      final error = jsonDecode(response.body);
      throw Exception(error['message'] ?? 'Request failed');
    }
  }
}

