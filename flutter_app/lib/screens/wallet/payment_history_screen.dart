import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/wallet_provider.dart';
import '../../models/payment.dart';
import 'package:intl/intl.dart';

class PaymentHistoryScreen extends StatefulWidget {
  const PaymentHistoryScreen({super.key});

  @override
  State<PaymentHistoryScreen> createState() => _PaymentHistoryScreenState();
}

class _PaymentHistoryScreenState extends State<PaymentHistoryScreen> {
  PaymentType? _filterType;

  @override
  Widget build(BuildContext context) {
    final walletProvider = Provider.of<WalletProvider>(context);
    final payments = _filterType != null
        ? walletProvider.getPaymentsByType(_filterType!)
        : walletProvider.payments;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Payment History'),
        actions: [
          PopupMenuButton<PaymentType?>(
            icon: const Icon(Icons.filter_list),
            onSelected: (type) {
              setState(() {
                _filterType = type;
              });
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: null,
                child: Text('All'),
              ),
              const PopupMenuItem(
                value: PaymentType.earnings,
                child: Text('Earnings'),
              ),
              const PopupMenuItem(
                value: PaymentType.withdrawal,
                child: Text('Withdrawals'),
              ),
              const PopupMenuItem(
                value: PaymentType.bonus,
                child: Text('Bonuses'),
              ),
              const PopupMenuItem(
                value: PaymentType.deduction,
                child: Text('Deductions'),
              ),
            ],
          ),
        ],
      ),
      body: payments.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.receipt_long, size: 64, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text(
                    'No transactions found',
                    style: TextStyle(fontSize: 16, color: Colors.grey[600]),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: payments.length,
              itemBuilder: (context, index) {
                final payment = payments[index];
                return _buildPaymentCard(payment);
              },
            ),
    );
  }

  Widget _buildPaymentCard(Payment payment) {
    final isCredit = payment.type == PaymentType.earnings ||
        payment.type == PaymentType.bonus;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: isCredit
                      ? Colors.green.withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  child: Icon(
                    _getPaymentIcon(payment.type),
                    color: isCredit ? Colors.green : Colors.red,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        payment.clientName,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        _getPaymentTypeText(payment.type),
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                Text(
                  '${isCredit ? '+' : '-'}\$${payment.amount.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: isCredit ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text(
                      DateFormat('MMM d, yyyy').format(payment.date),
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text(
                      DateFormat('h:mm a').format(payment.date),
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ],
                ),
                _buildStatusChip(payment.status),
              ],
            ),
            if (payment.transactionId != null) ...[
              const SizedBox(height: 8),
              Text(
                'Transaction ID: ${payment.transactionId}',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  IconData _getPaymentIcon(PaymentType type) {
    switch (type) {
      case PaymentType.earnings:
        return Icons.attach_money;
      case PaymentType.withdrawal:
        return Icons.arrow_upward;
      case PaymentType.bonus:
        return Icons.card_giftcard;
      case PaymentType.deduction:
        return Icons.remove_circle;
    }
  }

  String _getPaymentTypeText(PaymentType type) {
    switch (type) {
      case PaymentType.earnings:
        return 'Job Earnings';
      case PaymentType.withdrawal:
        return 'Withdrawal';
      case PaymentType.bonus:
        return 'Bonus';
      case PaymentType.deduction:
        return 'Deduction';
    }
  }

  Widget _buildStatusChip(PaymentStatus status) {
    Color color;
    String text;

    switch (status) {
      case PaymentStatus.pending:
        color = Colors.orange;
        text = 'Pending';
        break;
      case PaymentStatus.completed:
        color = Colors.green;
        text = 'Completed';
        break;
      case PaymentStatus.failed:
        color = Colors.red;
        text = 'Failed';
        break;
      case PaymentStatus.refunded:
        color = Colors.purple;
        text = 'Refunded';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

