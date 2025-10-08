import 'package:flutter/foundation.dart';
import '../models/cleaner.dart';
import '../services/api_service.dart';
import '../services/storage_service.dart';
import '../config/api_config.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final StorageService _storageService = StorageService();

  Cleaner? _currentUser;
  bool _isLoading = false;
  String? _errorMessage;

  Cleaner? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _currentUser != null;

  Future<void> checkAuthStatus() async {
    _isLoading = true;

    try {
      final isLoggedIn = await _storageService.isLoggedIn();
      if (isLoggedIn) {
        _currentUser = await _storageService.getUser();
        // Don't call refreshProfile during initial check to avoid network errors
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // DEMO MODE - Works without backend
      if (email == 'demo@example.com' && password == 'demo123') {
        print('DEMO LOGIN: Starting demo login process');
        await Future.delayed(const Duration(seconds: 1)); // Simulate network delay
        _currentUser = Cleaner(
          id: 'demo_cleaner_1',
          name: 'Demo Cleaner',
          email: 'demo@example.com',
          phone: '+1234567890',
          rating: 4.8,
          completedJobs: 127,
          isActive: true,
          createdAt: DateTime.now().subtract(const Duration(days: 365)),
        );
        await _storageService.saveUser(_currentUser!);
        await _storageService.saveToken('demo_token_123');
        _isLoading = false;
        notifyListeners();
        print('DEMO LOGIN: Demo login successful');
        return true;
      }

      // Real backend login
      final response = await _apiService.post(
        ApiConfig.loginEndpoint,
        {
          'email': email,
          'password': password,
        },
      );

      if (response['token'] != null && response['user'] != null) {
        await _storageService.saveToken(response['token']);
        _currentUser = Cleaner.fromJson(response['user']);
        await _storageService.saveUser(_currentUser!);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        throw Exception('Invalid response from server');
      }
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register(
    String name,
    String email,
    String phone,
    String password,
  ) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.post(
        ApiConfig.registerEndpoint,
        {
          'name': name,
          'email': email,
          'phone': phone,
          'password': password,
        },
      );

      if (response['token'] != null && response['user'] != null) {
        await _storageService.saveToken(response['token']);
        _currentUser = Cleaner.fromJson(response['user']);
        await _storageService.saveUser(_currentUser!);
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        throw Exception('Invalid response from server');
      }
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> refreshProfile() async {
    try {
      final response = await _apiService.get(ApiConfig.profileEndpoint);
      if (response['user'] != null) {
        _currentUser = Cleaner.fromJson(response['user']);
        await _storageService.saveUser(_currentUser!);
        notifyListeners();
      }
    } catch (e) {
      print('Error refreshing profile: $e');
    }
  }

  Future<void> logout() async {
    await _storageService.clearAll();
    _currentUser = null;
    _errorMessage = null;
    notifyListeners();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}

