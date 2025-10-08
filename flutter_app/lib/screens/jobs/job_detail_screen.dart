import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../models/job.dart';
import '../../providers/job_provider.dart';
import '../../services/location_service.dart';
import 'package:intl/intl.dart';

class JobDetailScreen extends StatefulWidget {
  final Job job;

  const JobDetailScreen({super.key, required this.job});

  @override
  State<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends State<JobDetailScreen> {
  final _messageController = TextEditingController();
  final _etaController = TextEditingController();
  final _locationService = LocationService();

  @override
  void dispose() {
    _messageController.dispose();
    _etaController.dispose();
    super.dispose();
  }

  Future<void> _clockIn() async {
    final jobProvider = Provider.of<JobProvider>(context, listen: false);
    final success = await jobProvider.clockIn(widget.job.id);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Clocked in successfully' : 'Failed to clock in'),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    }
  }

  Future<void> _clockOut() async {
    final jobProvider = Provider.of<JobProvider>(context, listen: false);
    final success = await jobProvider.clockOut(widget.job.id);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Clocked out successfully' : 'Failed to clock out'),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
      if (success) {
        Navigator.of(context).pop();
      }
    }
  }

  Future<void> _updateETA() async {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Update ETA'),
        content: TextField(
          controller: _etaController,
          decoration: const InputDecoration(
            labelText: 'ETA (e.g., 15 minutes)',
            hintText: 'Enter estimated time of arrival',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final jobProvider = Provider.of<JobProvider>(context, listen: false);
              final success = await jobProvider.updateETA(
                widget.job.id,
                _etaController.text,
              );
              if (mounted) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'ETA updated' : 'Failed to update ETA'),
                    backgroundColor: success ? Colors.green : Colors.red,
                  ),
                );
              }
            },
            child: const Text('Update'),
          ),
        ],
      ),
    );
  }

  Future<void> _sendMessage() async {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Send Message to Client'),
        content: TextField(
          controller: _messageController,
          maxLines: 3,
          decoration: const InputDecoration(
            labelText: 'Message',
            hintText: 'Enter your message',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              final jobProvider = Provider.of<JobProvider>(context, listen: false);
              final success = await jobProvider.sendMessage(
                widget.job.id,
                _messageController.text,
              );
              if (mounted) {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success ? 'Message sent' : 'Failed to send message'),
                    backgroundColor: success ? Colors.green : Colors.red,
                  ),
                );
                _messageController.clear();
              }
            },
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }

  Future<void> _callClient() async {
    final Uri phoneUri = Uri(scheme: 'tel', path: widget.job.clientPhone);
    if (await canLaunchUrl(phoneUri)) {
      await launchUrl(phoneUri);
    }
  }

  @override
  Widget build(BuildContext context) {
    final job = Provider.of<JobProvider>(context)
            .jobs
            .firstWhere((j) => j.id == widget.job.id, orElse: () => widget.job);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.phone),
            onPressed: _callClient,
            tooltip: 'Call Client',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Job Status Card
            Card(
              color: _getStatusColor(job.status),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Icon(
                      _getStatusIcon(job.status),
                      color: Colors.white,
                      size: 32,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _getStatusText(job.status),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            job.serviceType,
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      '\$${job.price.toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Client Info
            _buildSectionCard(
              title: 'Client Information',
              icon: Icons.person,
              children: [
                _buildInfoRow('Name', job.clientName),
                _buildInfoRow('Phone', job.clientPhone),
                _buildInfoRow('Address', job.clientAddress),
              ],
            ),

            // Schedule Info
            _buildSectionCard(
              title: 'Schedule',
              icon: Icons.calendar_today,
              children: [
                _buildInfoRow(
                  'Date',
                  DateFormat('EEEE, MMMM d, y').format(job.scheduledDate),
                ),
                _buildInfoRow('Time', job.scheduledTime),
                if (job.eta != null) _buildInfoRow('ETA', job.eta!),
              ],
            ),

            // Tasks
            if (job.tasks.isNotEmpty)
              _buildSectionCard(
                title: 'Tasks',
                icon: Icons.checklist,
                children: job.tasks
                    .map((task) => CheckboxListTile(
                          title: Text(task.description),
                          value: task.isCompleted,
                          onChanged: job.status == JobStatus.inProgress
                              ? (value) {
                                  final jobProvider = Provider.of<JobProvider>(
                                      context,
                                      listen: false);
                                  jobProvider.updateTaskStatus(
                                    job.id,
                                    task.id,
                                    value ?? false,
                                  );
                                }
                              : null,
                        ))
                    .toList(),
              ),

            // Time tracking
            if (job.clockInTime != null || job.clockOutTime != null)
              _buildSectionCard(
                title: 'Time Tracking',
                icon: Icons.access_time,
                children: [
                  if (job.clockInTime != null)
                    _buildInfoRow(
                      'Clock In',
                      DateFormat('h:mm a').format(job.clockInTime!),
                    ),
                  if (job.clockOutTime != null)
                    _buildInfoRow(
                      'Clock Out',
                      DateFormat('h:mm a').format(job.clockOutTime!),
                    ),
                ],
              ),

            // Notes
            if (job.notes != null && job.notes!.isNotEmpty)
              _buildSectionCard(
                title: 'Notes',
                icon: Icons.note,
                children: [
                  Padding(
                    padding: const EdgeInsets.all(8),
                    child: Text(job.notes!),
                  ),
                ],
              ),
          ],
        ),
      ),
      bottomNavigationBar: _buildActionButtons(job),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: const Color(0xFF2196F3)),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(
                color: Colors.grey[600],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget? _buildActionButtons(Job job) {
    if (job.status == JobStatus.completed || job.status == JobStatus.cancelled) {
      return null;
    }

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
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (job.clockInTime == null)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _clockIn,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Clock In'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.all(16),
                ),
              ),
            )
          else if (job.clockOutTime == null)
            Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _updateETA,
                        icon: const Icon(Icons.access_time),
                        label: const Text('Update ETA'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _sendMessage,
                        icon: const Icon(Icons.message),
                        label: const Text('Message'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _clockOut,
                    icon: const Icon(Icons.stop),
                    label: const Text('Clock Out'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                      padding: const EdgeInsets.all(16),
                    ),
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Color _getStatusColor(JobStatus status) {
    switch (status) {
      case JobStatus.pending:
        return Colors.orange;
      case JobStatus.assigned:
        return Colors.blue;
      case JobStatus.inProgress:
        return Colors.green;
      case JobStatus.completed:
        return Colors.teal;
      case JobStatus.cancelled:
        return Colors.red;
    }
  }

  IconData _getStatusIcon(JobStatus status) {
    switch (status) {
      case JobStatus.pending:
        return Icons.pending;
      case JobStatus.assigned:
        return Icons.assignment;
      case JobStatus.inProgress:
        return Icons.play_circle;
      case JobStatus.completed:
        return Icons.check_circle;
      case JobStatus.cancelled:
        return Icons.cancel;
    }
  }

  String _getStatusText(JobStatus status) {
    switch (status) {
      case JobStatus.pending:
        return 'Pending';
      case JobStatus.assigned:
        return 'Assigned';
      case JobStatus.inProgress:
        return 'In Progress';
      case JobStatus.completed:
        return 'Completed';
      case JobStatus.cancelled:
        return 'Cancelled';
    }
  }
}

