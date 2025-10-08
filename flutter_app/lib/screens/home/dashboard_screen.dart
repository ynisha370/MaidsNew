import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/job_provider.dart';
import '../../providers/wallet_provider.dart';
import '../jobs/jobs_screen.dart';
import '../wallet/wallet_screen.dart';
import '../profile/profile_screen.dart';
import '../../widgets/dashboard_stats_card.dart';
import '../../widgets/job_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = [
    const DashboardHome(),
    const JobsScreen(),
    const WalletScreen(),
    const ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final jobProvider = Provider.of<JobProvider>(context, listen: false);
    final walletProvider = Provider.of<WalletProvider>(context, listen: false);
    
    await Future.wait([
      jobProvider.fetchJobs(),
      walletProvider.fetchWallet(),
      walletProvider.fetchEarnings(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF2196F3),
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.work),
            label: 'Jobs',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_balance_wallet),
            label: 'Wallet',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class DashboardHome extends StatelessWidget {
  const DashboardHome({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final jobProvider = Provider.of<JobProvider>(context);
    final walletProvider = Provider.of<WalletProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              // TODO: Navigate to notifications
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.wait([
            jobProvider.fetchJobs(),
            walletProvider.fetchWallet(),
            walletProvider.fetchEarnings(),
          ]);
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome section
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 30,
                        backgroundColor: const Color(0xFF2196F3),
                        child: Text(
                          authProvider.currentUser?.name
                                  .substring(0, 1)
                                  .toUpperCase() ??
                              'U',
                          style: const TextStyle(
                            fontSize: 24,
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Welcome back,',
                              style: TextStyle(
                                fontSize: 14,
                                color: Colors.grey[600],
                              ),
                            ),
                            Text(
                              authProvider.currentUser?.name ?? 'User',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Column(
                        children: [
                          const Icon(Icons.star, color: Colors.amber),
                          Text(
                            authProvider.currentUser?.rating.toStringAsFixed(1) ??
                                '0.0',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Stats cards
              Row(
                children: [
                  Expanded(
                    child: DashboardStatsCard(
                      title: 'Today\'s Jobs',
                      value: jobProvider.todayJobs.length.toString(),
                      icon: Icons.work,
                      color: Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DashboardStatsCard(
                      title: 'Completed',
                      value: authProvider.currentUser?.completedJobs.toString() ??
                          '0',
                      icon: Icons.check_circle,
                      color: Colors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: DashboardStatsCard(
                      title: 'Balance',
                      value: '\$${walletProvider.balance.toStringAsFixed(2)}',
                      icon: Icons.account_balance_wallet,
                      color: Colors.purple,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: DashboardStatsCard(
                      title: 'Total Earnings',
                      value:
                          '\$${walletProvider.totalEarnings.toStringAsFixed(2)}',
                      icon: Icons.attach_money,
                      color: Colors.orange,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Today's jobs
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Today\'s Jobs',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      // Switch to jobs tab
                    },
                    child: const Text('View All'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (jobProvider.isLoading)
                const Center(child: CircularProgressIndicator())
              else if (jobProvider.todayJobs.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(
                            Icons.event_available,
                            size: 48,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'No jobs scheduled for today',
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
                  itemCount: jobProvider.todayJobs.length,
                  itemBuilder: (context, index) {
                    return JobCard(job: jobProvider.todayJobs[index]);
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }
}

