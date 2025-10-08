class Payment {
  final String id;
  final String jobId;
  final String clientName;
  final double amount;
  final PaymentStatus status;
  final PaymentType type;
  final DateTime date;
  final String? transactionId;
  final String? notes;

  Payment({
    required this.id,
    required this.jobId,
    required this.clientName,
    required this.amount,
    required this.status,
    required this.type,
    required this.date,
    this.transactionId,
    this.notes,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['_id'] ?? json['id'] ?? '',
      jobId: json['jobId'] ?? '',
      clientName: json['clientName'] ?? '',
      amount: (json['amount'] ?? 0.0).toDouble(),
      status: PaymentStatus.values.firstWhere(
        (e) => e.toString() == 'PaymentStatus.${json['status']}',
        orElse: () => PaymentStatus.pending,
      ),
      type: PaymentType.values.firstWhere(
        (e) => e.toString() == 'PaymentType.${json['type']}',
        orElse: () => PaymentType.earnings,
      ),
      date: json['date'] != null
          ? DateTime.parse(json['date'])
          : DateTime.now(),
      transactionId: json['transactionId'],
      notes: json['notes'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'jobId': jobId,
      'clientName': clientName,
      'amount': amount,
      'status': status.toString().split('.').last,
      'type': type.toString().split('.').last,
      'date': date.toIso8601String(),
      'transactionId': transactionId,
      'notes': notes,
    };
  }
}

enum PaymentStatus {
  pending,
  completed,
  failed,
  refunded,
}

enum PaymentType {
  earnings,
  withdrawal,
  bonus,
  deduction,
}

class Wallet {
  final String id;
  final String cleanerId;
  final double balance;
  final double totalEarnings;
  final double totalWithdrawals;
  final List<Payment> recentTransactions;

  Wallet({
    required this.id,
    required this.cleanerId,
    this.balance = 0.0,
    this.totalEarnings = 0.0,
    this.totalWithdrawals = 0.0,
    this.recentTransactions = const [],
  });

  factory Wallet.fromJson(Map<String, dynamic> json) {
    return Wallet(
      id: json['_id'] ?? json['id'] ?? '',
      cleanerId: json['cleanerId'] ?? '',
      balance: (json['balance'] ?? 0.0).toDouble(),
      totalEarnings: (json['totalEarnings'] ?? 0.0).toDouble(),
      totalWithdrawals: (json['totalWithdrawals'] ?? 0.0).toDouble(),
      recentTransactions: json['recentTransactions'] != null
          ? (json['recentTransactions'] as List)
              .map((t) => Payment.fromJson(t))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'cleanerId': cleanerId,
      'balance': balance,
      'totalEarnings': totalEarnings,
      'totalWithdrawals': totalWithdrawals,
      'recentTransactions':
          recentTransactions.map((t) => t.toJson()).toList(),
    };
  }
}

