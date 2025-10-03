import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../services/job_service.dart';
import '../utils/app_theme.dart';

class HomeScreenClean extends StatefulWidget {
  const HomeScreenClean({super.key});

  @override
  State<HomeScreenClean> createState() => _HomeScreenCleanState();
}

class _HomeScreenCleanState extends State<HomeScreenClean> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Maids of Cyfair - Cleaner'),
        backgroundColor: AppTheme.primaryColor,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _logout(),
          ),
        ],
      ),
      body: IndexedStack(
        index: _selectedIndex,
        children: [
          _buildTodayTab(),
          _buildAllJobsTab(),
          _buildProfileTab(),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        selectedItemColor: AppTheme.primaryColor,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.today),
            label: 'Today',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.work),
            label: 'All Jobs',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }

  Widget _buildTodayTab() {
    return Consumer<JobService>(
      builder: (context, jobService, child) {
        if (jobService.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        final todaysJobs = jobService.todaysJobs;
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Today\'s Jobs',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primaryColor,
                ),
              ),
              const SizedBox(height: 16),
              if (todaysJobs.isEmpty)
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        Icon(
                          Icons.work_off,
                          size: 48,
                          color: AppTheme.gray400,
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'No jobs scheduled for today',
                          style: TextStyle(
                            fontSize: 16,
                            color: AppTheme.gray600,
                          ),
                        ),
                      ],
                    ),
                  ),
                )
              else
                ...todaysJobs.map((job) => _buildJobCard(job)),
            ],
          ),
        );
      },
    );
  }

  Widget _buildAllJobsTab() {
    return Consumer<JobService>(
      builder: (context, jobService, child) {
        if (jobService.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'All Jobs',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppTheme.primaryColor,
                ),
              ),
              const SizedBox(height: 16),
              _buildJobsList(jobService.upcomingJobs),
              const SizedBox(height: 16),
              _buildJobsList(jobService.completedJobs),
              const SizedBox(height: 16),
              _buildJobsList(jobService.jobs),
            ],
          ),
        );
      },
    );
  }

  Widget _buildProfileTab() {
    return Consumer<AuthService>(
      builder: (context, authService, child) {
        final cleaner = authService.currentCleaner;
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: AppTheme.primaryColor,
                        child: Text(
                          cleaner?.firstName.substring(0, 1).toUpperCase() ?? 'C',
                          style: const TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        '${cleaner?.firstName ?? 'Cleaner'} ${cleaner?.lastName ?? 'Name'}',
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        cleaner?.email ?? 'cleaner@maids.com',
                        style: const TextStyle(
                          fontSize: 16,
                          color: AppTheme.gray600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Statistics',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      Consumer<JobService>(
                        builder: (context, jobService, child) {
                          final totalJobs = jobService.jobs.length;
                          final completedJobs = jobService.completedJobs.length;
                          
                          return Row(
                            children: [
                              Expanded(
                                child: _buildStatCard(
                                  'Total Jobs',
                                  totalJobs.toString(),
                                  Icons.work,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: _buildStatCard(
                                  'Completed',
                                  completedJobs.toString(),
                                  Icons.check_circle,
                                ),
                              ),
                            ],
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildJobCard(dynamic job) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getStatusColor(job.status),
          child: Icon(
            _getStatusIcon(job.status),
            color: Colors.white,
          ),
        ),
        title: Text('Job #${job.id.substring(0, 8)}'),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Customer: ${job.customerId.substring(0, 8)}'),
            Text('Time: ${job.timeSlot}'),
            Text('Status: ${job.statusDisplayName}'),
          ],
        ),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: () => _navigateToJobDetail(job),
      ),
    );
  }

  Widget _buildJobsList(List<dynamic> jobs) {
    if (jobs.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No jobs found'),
        ),
      );
    }

    return Column(
      children: jobs.map((job) => _buildJobCard(job)).toList(),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.primaryColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: AppTheme.primaryColor),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: AppTheme.primaryColor,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: AppTheme.gray600,
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return AppTheme.warningColor;
      case 'confirmed':
        return AppTheme.infoColor;
      case 'in_progress':
        return AppTheme.primaryColor;
      case 'completed':
        return AppTheme.successColor;
      default:
        return AppTheme.gray400;
    }
  }

  IconData _getStatusIcon(String status) {
    switch (status) {
      case 'pending':
        return Icons.schedule;
      case 'confirmed':
        return Icons.check;
      case 'in_progress':
        return Icons.play_arrow;
      case 'completed':
        return Icons.done;
      default:
        return Icons.help;
    }
  }

  void _navigateToJobDetail(dynamic job) {
    final jobService = context.read<JobService>();
    jobService.selectJob(job);
    Navigator.of(context).pushNamed('/job-detail');
  }

  void _logout() {
    final authService = context.read<AuthService>();
    authService.logout();
    Navigator.of(context).pushReplacementNamed('/login');
  }
}
