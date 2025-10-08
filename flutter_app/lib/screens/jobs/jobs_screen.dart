import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/job_provider.dart';
import '../../widgets/job_card.dart';
import '../../models/job.dart';

class JobsScreen extends StatefulWidget {
  const JobsScreen({super.key});

  @override
  State<JobsScreen> createState() => _JobsScreenState();
}

class _JobsScreenState extends State<JobsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final jobProvider = Provider.of<JobProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Jobs'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Today'),
            Tab(text: 'Upcoming'),
            Tab(text: 'Completed'),
          ],
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => jobProvider.fetchJobs(),
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildJobList(jobProvider.todayJobs, 'No jobs for today'),
            _buildJobList(jobProvider.upcomingJobs, 'No upcoming jobs'),
            _buildJobList(jobProvider.completedJobs, 'No completed jobs'),
          ],
        ),
      ),
    );
  }

  Widget _buildJobList(List<Job> jobs, String emptyMessage) {
    if (jobs.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              emptyMessage,
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: jobs.length,
      itemBuilder: (context, index) {
        return JobCard(job: jobs[index]);
      },
    );
  }
}

