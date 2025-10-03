import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.44.141:8000/api';
  
  String? _authToken;
  
  // Auth Token Management
  String? get authToken => _authToken;
  
  void setAuthToken(String token) {
    _authToken = token;
  }
  
  Future<void> saveToken(String token) async {
    _authToken = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
  }
  
  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }
  
  Future<void> clearToken() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
  
  // HTTP Headers
  Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }
  
  // API Methods
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: _headers,
        body: jsonEncode({
          'email': email,
          'password': password,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await saveToken(data['access_token']);
        return {'success': true, 'data': data};
      } else {
        final error = jsonDecode(response.body);
        return {'success': false, 'error': error['detail'] ?? 'Login failed'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  Future<Map<String, dynamic>> getCurrentUser() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/auth/me'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to get user info'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  Future<Map<String, dynamic>> getCleanerJobs(String cleanerId) async {
    try {
      // For now, we'll use the regular bookings endpoint and filter client-side
      // In a production app, you'd want a dedicated cleaner endpoint
      final response = await http.get(
        Uri.parse('$baseUrl/bookings'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        final allBookings = jsonDecode(response.body) as List;
        // Filter bookings assigned to this cleaner
        final cleanerJobs = allBookings
            .where((booking) => booking['cleaner_id'] == cleanerId)
            .toList();
        return {'success': true, 'data': cleanerJobs};
      } else {
        return {'success': false, 'error': 'Failed to load jobs'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  Future<Map<String, dynamic>> updateJobStatus(String jobId, String status) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/admin/bookings/$jobId'),
        headers: _headers,
        body: jsonEncode({'status': status}),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to update job status'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  Future<Map<String, dynamic>> getCustomerDetails(String customerId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/customers/$customerId'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to load customer details'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Create cleaner account (this should be called by admin)
  Future<Map<String, dynamic>> createCleanerAccount(Map<String, dynamic> cleanerData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/admin/cleaners'),
        headers: _headers,
        body: jsonEncode(cleanerData),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to create cleaner account'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  Future<Map<String, dynamic>> getAllCleaners() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/admin/cleaners'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to load cleaners'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Update job progress
  Future<Map<String, dynamic>> updateJobProgress(String jobId, Map<String, dynamic> progressData) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/admin/bookings/$jobId/progress'),
        headers: _headers,
        body: jsonEncode(progressData),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to update job progress'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Update job checklist
  Future<Map<String, dynamic>> updateJobChecklist(String jobId, List<Map<String, dynamic>> checklist) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/admin/bookings/$jobId/checklist'),
        headers: _headers,
        body: jsonEncode({'checklist': checklist}),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to update job checklist'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Update job ETA
  Future<Map<String, dynamic>> updateJobETA(String jobId, String eta) async {
    try {
      final response = await http.patch(
        Uri.parse('$baseUrl/admin/bookings/$jobId/eta'),
        headers: _headers,
        body: jsonEncode({'eta': eta}),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to update job ETA'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Upload job photos
  Future<Map<String, dynamic>> uploadJobPhotos(String jobId, List<String> photoPaths) async {
    try {
      // In a real implementation, this would use multipart/form-data
      // For now, we'll simulate the upload
      await Future.delayed(const Duration(seconds: 2));
      return {'success': true, 'data': {'uploaded_photos': photoPaths.length}};
    } catch (e) {
      return {'success': false, 'error': 'Failed to upload photos: ${e.toString()}'};
    }
  }
  
  // Get job photos
  Future<Map<String, dynamic>> getJobPhotos(String jobId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/admin/bookings/$jobId/photos'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to load job photos'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Send notification to customer
  Future<Map<String, dynamic>> sendCustomerNotification(String customerId, String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/admin/notifications/send'),
        headers: _headers,
        body: jsonEncode({
          'customer_id': customerId,
          'message': message,
          'type': 'cleaner_update'
        }),
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to send notification'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
  
  // Get cleaner statistics
  Future<Map<String, dynamic>> getCleanerStats(String cleanerId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/admin/cleaners/$cleanerId/stats'),
        headers: _headers,
      );
      
      if (response.statusCode == 200) {
        return {'success': true, 'data': jsonDecode(response.body)};
      } else {
        return {'success': false, 'error': 'Failed to load cleaner stats'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Network error: ${e.toString()}'};
    }
  }
}