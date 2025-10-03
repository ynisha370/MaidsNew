import 'package:flutter/material.dart';
import 'api_service.dart';
import '../models/customer.dart';

class CustomerService extends ChangeNotifier {
  final ApiService _apiService;
  
  Map<String, Customer> _customers = {};
  bool _isLoading = false;
  String? _errorMessage;
  
  CustomerService(this._apiService);
  
  // Getters
  Map<String, Customer> get customers => _customers;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  
  // Get customer by ID
  Customer? getCustomerById(String customerId) {
    return _customers[customerId];
  }
  
  // Load customer details
  Future<Customer?> loadCustomerDetails(String customerId) async {
    // Check if we already have the customer cached
    if (_customers.containsKey(customerId)) {
      return _customers[customerId];
    }
    
    _setLoading(true);
    _clearError();
    
    try {
      final result = await _apiService.getCustomerDetails(customerId);
      
      if (result['success']) {
        final customerData = result['data'];
        final customer = Customer.fromJson(customerData);
        _customers[customerId] = customer;
        notifyListeners();
        return customer;
      } else {
        _setError(result['error']);
        return null;
      }
    } catch (e) {
      _setError('Failed to load customer details: ${e.toString()}');
      return null;
    } finally {
      _setLoading(false);
    }
  }
  
  // Contact customer (phone call)
  Future<void> contactCustomer(String customerId, String phoneNumber) async {
    // In a real implementation, this would use url_launcher to make a phone call
    // For now, we'll just show a success message
    _clearError();
    notifyListeners();
  }
  
  // Send message to customer (SMS)
  Future<void> sendMessageToCustomer(String customerId, String phoneNumber, String message) async {
    // In a real implementation, this would use url_launcher to send SMS
    // For now, we'll just show a success message
    _clearError();
    notifyListeners();
  }
  
  // Helper methods
  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }
  
  void _setError(String error) {
    _errorMessage = error;
    notifyListeners();
  }
  
  void _clearError() {
    _errorMessage = null;
  }
  
  void clearError() {
    _clearError();
    notifyListeners();
  }
}
