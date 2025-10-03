import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/notification_service.dart';
import '../utils/app_theme.dart';

class NotificationWidget extends StatelessWidget {
  final String customerId;
  final String customerName;
  
  const NotificationWidget({
    super.key,
    required this.customerId,
    required this.customerName,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<NotificationService>(
      builder: (context, notificationService, child) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(
                      Icons.notifications,
                      color: AppTheme.primaryColor,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    const Text(
                      'Customer Communication',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                const Text(
                  'Send updates to customer',
                  style: TextStyle(
                    fontSize: 14,
                    color: AppTheme.gray600,
                  ),
                ),
                
                const SizedBox(height: 16),
                
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _sendETAUpdate(context, notificationService),
                        icon: const Icon(Icons.schedule, size: 18),
                        label: const Text('Send ETA'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _sendArrivalUpdate(context, notificationService),
                        icon: const Icon(Icons.location_on, size: 18),
                        label: const Text('Arrived'),
                      ),
                    ),
                  ],
                ),
                
                const SizedBox(height: 12),
                
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _sendProgressUpdate(context, notificationService),
                        icon: const Icon(Icons.work, size: 18),
                        label: const Text('Progress'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _sendCompletionUpdate(context, notificationService),
                        icon: const Icon(Icons.check_circle, size: 18),
                        label: const Text('Complete'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  void _sendETAUpdate(BuildContext context, NotificationService notificationService) {
    _showMessageDialog(
      context,
      'Send ETA Update',
      'Enter your estimated arrival time:',
      (message) => _sendNotification(notificationService, 'ETA Update: $message'),
    );
  }
  
  void _sendArrivalUpdate(BuildContext context, NotificationService notificationService) {
    _sendNotification(notificationService, 'I have arrived at your location and am ready to begin the cleaning service.');
  }
  
  void _sendProgressUpdate(BuildContext context, NotificationService notificationService) {
    _showMessageDialog(
      context,
      'Send Progress Update',
      'Enter your progress update:',
      (message) => _sendNotification(notificationService, 'Progress Update: $message'),
    );
  }
  
  void _sendCompletionUpdate(BuildContext context, NotificationService notificationService) {
    _sendNotification(notificationService, 'The cleaning service has been completed. Thank you for choosing Maids of Cyfair!');
  }
  
  void _showMessageDialog(
    BuildContext context,
    String title,
    String hint,
    Function(String) onSend,
  ) {
    final controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: TextField(
            controller: controller,
            decoration: InputDecoration(
              hintText: hint,
              border: const OutlineInputBorder(),
            ),
            maxLines: 3,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (controller.text.trim().isNotEmpty) {
                  onSend(controller.text.trim());
                  Navigator.of(context).pop();
                }
              },
              child: const Text('Send'),
            ),
          ],
        );
      },
    );
  }
  
  void _sendNotification(NotificationService notificationService, String message) async {
    final success = await notificationService.sendCustomerNotification(customerId, message);
    
    if (success) {
      // Show success message
      // In a real app, you would show a snackbar or toast
      print('Notification sent successfully');
    } else {
      // Show error message
      print('Failed to send notification: ${notificationService.errorMessage}');
    }
  }
}
