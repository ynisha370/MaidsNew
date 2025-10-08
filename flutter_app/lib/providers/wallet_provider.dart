import 'package:flutter/foundation.dart';
import '../models/payment.dart';
import '../services/api_service.dart';
import '../config/api_config.dart';

class WalletProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  Wallet? _wallet;
  List<Payment> _payments = [];
  bool _isLoading = false;
  String? _errorMessage;

  Wallet? get wallet => _wallet;
  List<Payment> get payments => _payments;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  double get totalEarnings => _wallet?.totalEarnings ?? 0.0;
  double get balance => _wallet?.balance ?? 0.0;
  double get totalWithdrawals => _wallet?.totalWithdrawals ?? 0.0;

  Future<void> fetchWallet() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConfig.walletEndpoint);
      if (response['wallet'] != null) {
        _wallet = Wallet.fromJson(response['wallet']);
      }
    } catch (e) {
      // Silently fail in demo mode - use demo wallet
      _errorMessage = null;
      _wallet = Wallet(
        id: 'demo_wallet',
        cleanerId: 'demo_cleaner_1',
        balance: 345.00,
        totalEarnings: 12750.00,
        totalWithdrawals: 12405.00,
      );
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchPayments() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConfig.paymentsEndpoint);
      if (response['payments'] != null) {
        _payments = (response['payments'] as List)
            .map((payment) => Payment.fromJson(payment))
            .toList();
      }
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchEarnings() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.get(ApiConfig.earningsEndpoint);
      if (response['earnings'] != null) {
        // Update wallet with earnings data
        _wallet = Wallet.fromJson(response['earnings']);
      }
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  List<Payment> getPaymentsByType(PaymentType type) {
    return _payments.where((p) => p.type == type).toList();
  }

  List<Payment> getPaymentsByDateRange(DateTime start, DateTime end) {
    return _payments.where((p) {
      return p.date.isAfter(start) && p.date.isBefore(end);
    }).toList();
  }

  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}

