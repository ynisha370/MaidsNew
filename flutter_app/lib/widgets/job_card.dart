import 'package:flutter/material.dart';
import '../models/job.dart';
import '../screens/jobs/job_detail_screen.dart';
import 'package:intl/intl.dart';

class JobCard extends StatelessWidget {
  final Job job;

  const JobCard({super.key, required this.job});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => JobDetailScreen(job: job),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          job.clientName,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          job.serviceType,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: _getStatusColor(job.status).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _getStatusText(job.status),
                      style: TextStyle(
                        color: _getStatusColor(job.status),
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    DateFormat('MMM d, yyyy').format(job.scheduledDate),
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(width: 16),
                  Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    job.scheduledTime,
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.location_on, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      job.clientAddress,
                      style: TextStyle(color: Colors.grey[600]),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              const Divider(height: 1),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  if (job.tasks.isNotEmpty)
                    Row(
                      children: [
                        Icon(Icons.checklist, size: 16, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          '${job.tasks.where((t) => t.isCompleted).length}/${job.tasks.length} tasks',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ],
                    ),
                  const Spacer(),
                  Text(
                    '\$${job.price.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2196F3),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
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

