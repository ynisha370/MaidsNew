import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/job_service.dart';
import '../utils/app_theme.dart';

class JobDetailScreenClean extends StatefulWidget {
  const JobDetailScreenClean({super.key});

  @override
  State<JobDetailScreenClean> createState() => _JobDetailScreenCleanState();
}

class _JobDetailScreenCleanState extends State<JobDetailScreenClean>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _etaController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _etaController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<JobService>(
      builder: (context, jobService, child) {
        final job = jobService.selectedJob;

        if (job == null) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('Job Details'),
            ),
            body: const Center(
              child: Text('No job selected'),
            ),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: Text('Job #${job.id.substring(0, 8)}'),
            actions: [
              IconButton(
                icon: const Icon(Icons.phone),
                onPressed: () => _makePhoneCall(job),
              ),
            ],
          ),
          body: Column(
            children: [
              // Job Status Bar
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                color: _getStatusColor(job.status).withOpacity(0.1),
                child: Row(
                  children: [
                    Icon(
                      _getStatusIcon(job.status),
                      color: _getStatusColor(job.status),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      job.statusDisplayName,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: _getStatusColor(job.status),
                      ),
                    ),
                    const Spacer(),
                    if (job.progress != null)
                      Text(
                        '${job.progress!.completionPercentage.round()}% Complete',
                        style: TextStyle(
                          fontSize: 14,
                          color: _getStatusColor(job.status),
                        ),
                      ),
                  ],
                ),
              ),

              // Tab Bar
              TabBar(
                controller: _tabController,
                labelColor: AppTheme.primaryColor,
                unselectedLabelColor: AppTheme.gray500,
                indicatorColor: AppTheme.primaryColor,
                tabs: const [
                  Tab(text: 'Details'),
                  Tab(text: 'Checklist'),
                  Tab(text: 'Timer'),
                ],
              ),

              // Tab Content
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    _buildDetailsTab(job),
                    _buildChecklistTab(job),
                    _buildTimerTab(job),
                  ],
                ),
              ),
            ],
          ),
          bottomNavigationBar: _buildBottomActions(job),
        );
      },
    );
  }

  Widget _buildDetailsTab(dynamic job) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Customer Info Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.person, color: AppTheme.primaryColor),
                      const SizedBox(width: 8),
                      const Text(
                        'Customer Information',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _buildInfoRow('Customer ID', job.customerId.substring(0, 8)),
                  _buildInfoRow('Booking Date', _formatDate(job.bookingDate)),
                  _buildInfoRow('Time Slot', job.timeSlot),
                  if (job.specialInstructions != null)
                    _buildInfoRow('Special Instructions', job.specialInstructions!),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // ETA Update Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.schedule, color: AppTheme.primaryColor),
                      const SizedBox(width: 8),
                      const Text(
                        'Update ETA',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _etaController,
                          decoration: const InputDecoration(
                            hintText: 'e.g., Arriving in 15 minutes',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: () => _updateETA(job),
                        child: const Text('Update'),
                      ),
                    ],
                  ),
                  if (job.eta != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: AppTheme.successColor.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Current ETA: ${job.eta}',
                        style: const TextStyle(
                          color: AppTheme.successColor,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChecklistTab(dynamic job) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Job Checklist',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          if (job.checklist != null && job.checklist!.isNotEmpty)
            ...job.checklist!.map((item) => _buildChecklistItem(item))
          else
            const Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Text('No checklist items available'),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildTimerTab(dynamic job) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const Text(
            'Job Timer',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text(
                    'Work Duration',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _getWorkDuration(job),
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () => _startJob(job),
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('Start'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.successColor,
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: () => _pauseJob(job),
                        icon: const Icon(Icons.pause),
                        label: const Text('Pause'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.warningColor,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChecklistItem(dynamic item) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Checkbox(
          value: item.isCompleted,
          onChanged: (value) => _toggleChecklistItem(item, value ?? false),
        ),
        title: Text(item.title),
        subtitle: item.description != null ? Text(item.description!) : null,
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              '$label:',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppTheme.gray700,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: AppTheme.gray800,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomActions(dynamic job) {
    final jobService = context.read<JobService>();
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          if (job.status == 'confirmed')
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _startJob(job),
                icon: const Icon(Icons.play_arrow),
                label: const Text('Start Job'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.successColor,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          if (job.status == 'in_progress') ...[
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _pauseJob(job),
                icon: const Icon(Icons.pause),
                label: const Text('Pause'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.warningColor,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () => _completeJob(job),
                icon: const Icon(Icons.check),
                label: const Text('Complete'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.successColor,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(String dateString) {
    try {
      final date = DateTime.parse(dateString);
      return DateFormat('MMM dd, yyyy').format(date);
    } catch (e) {
      return dateString;
    }
  }

  String _getWorkDuration(dynamic job) {
    if (job.clockInTime != null && job.clockOutTime != null) {
      final duration = job.clockOutTime.difference(job.clockInTime);
      final hours = duration.inHours;
      final minutes = duration.inMinutes % 60;
      return '${hours}h ${minutes}m';
    } else if (job.clockInTime != null) {
      final duration = DateTime.now().difference(job.clockInTime);
      final hours = duration.inHours;
      final minutes = duration.inMinutes % 60;
      return '${hours}h ${minutes}m (ongoing)';
    }
    return '0h 0m';
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

  void _startJob(dynamic job) {
    final jobService = context.read<JobService>();
    jobService.clockIn(job.id);
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Job started successfully!'),
        backgroundColor: AppTheme.successColor,
      ),
    );
  }

  void _pauseJob(dynamic job) {
    final jobService = context.read<JobService>();
    jobService.updateJobStatus(job.id, 'confirmed');
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Job paused'),
        backgroundColor: AppTheme.warningColor,
      ),
    );
  }

  void _completeJob(dynamic job) {
    final jobService = context.read<JobService>();
    jobService.clockOut(job.id);
    jobService.updateJobStatus(job.id, 'completed');
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Job completed successfully!'),
        backgroundColor: AppTheme.successColor,
      ),
    );
  }

  void _updateETA(dynamic job) {
    if (_etaController.text.isNotEmpty) {
      final jobService = context.read<JobService>();
      jobService.updateETA(job.id, _etaController.text);
      _etaController.clear();
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('ETA updated successfully!'),
          backgroundColor: AppTheme.successColor,
        ),
      );
    }
  }

  void _makePhoneCall(dynamic job) async {
    // For demo purposes, we'll show a dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Call Customer'),
        content: const Text('This would open the phone app to call the customer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _toggleChecklistItem(dynamic item, bool value) {
    // Update checklist item
    setState(() {
      item.isCompleted = value;
    });
  }
}
