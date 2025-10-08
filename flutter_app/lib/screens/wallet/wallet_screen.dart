import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/wallet_provider.dart';
import '../../models/payment.dart';
import 'payment_history_screen.dart';
import 'package:intl/intl.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final walletProvider = Provider.of<WalletProvider>(context, listen: false);
    await Future.wait([
      walletProvider.fetchWallet(),
      walletProvider.fetchPayments(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final walletProvider = Provider.of<WalletProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Wallet'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const PaymentHistoryScreen(),
                ),
              );
            },
            tooltip: 'Payment History',
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Balance Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF2196F3), Color(0xFF1976D2)],
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.blue.withOpacity(0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Current Balance',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '\$${walletProvider.balance.toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 40,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildBalanceInfo(
                          'Total Earned',
                          '\$${walletProvider.totalEarnings.toStringAsFixed(2)}',
                        ),
                        _buildBalanceInfo(
                          'Withdrawn',
                          '\$${walletProvider.totalWithdrawals.toStringAsFixed(2)}',
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Quick Actions
              Row(
                children: [
                  Expanded(
                    child: _buildActionButton(
                      'Withdraw',
                      Icons.arrow_upward,
                      Colors.orange,
                      () => _showWithdrawDialog(),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildActionButton(
                      'View History',
                      Icons.history,
                      Colors.blue,
                      () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (context) => const PaymentHistoryScreen(),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Recent Transactions
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Recent Transactions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const PaymentHistoryScreen(),
                        ),
                      );
                    },
                    child: const Text('See All'),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              if (walletProvider.isLoading)
                const Center(child: CircularProgressIndicator())
              else if (walletProvider.payments.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(
                            Icons.receipt_long,
                            size: 48,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'No transactions yet',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: walletProvider.payments.take(5).length,
                  itemBuilder: (context, index) {
                    final payment = walletProvider.payments[index];
                    return _buildTransactionCard(payment);
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBalanceInfo(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTransactionCard(Payment payment) {
    final isCredit = payment.type == PaymentType.earnings ||
        payment.type == PaymentType.bonus;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor:
              isCredit ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1),
          child: Icon(
            isCredit ? Icons.arrow_downward : Icons.arrow_upward,
            color: isCredit ? Colors.green : Colors.red,
          ),
        ),
        title: Text(
          payment.clientName,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          DateFormat('MMM d, yyyy • h:mm a').format(payment.date),
        ),
        trailing: Text(
          '${isCredit ? '+' : '-'}\$${payment.amount.toStringAsFixed(2)}',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: isCredit ? Colors.green : Colors.red,
          ),
        ),
      ),
    );
  }

  void _showWithdrawDialog() {
    final amountController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Withdraw Funds'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Available Balance: \$${Provider.of<WalletProvider>(context, listen: false).balance.toStringAsFixed(2)}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: amountController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Amount',
                prefixText: '\$',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              // TODO: Implement withdrawal
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Withdrawal request submitted'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: const Text('Withdraw'),
          ),
        ],
      ),
    );
  }
}

