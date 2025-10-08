import '../models/cleaner.dart';
import '../models/job.dart';
import '../models/payment.dart';

class DemoData {
  static Cleaner getDemoCleaner() {
    return Cleaner(
      id: 'demo_cleaner_1',
      name: 'John Doe',
      email: 'john@example.com',
      phone: '+1234567890',
      rating: 4.8,
      completedJobs: 127,
      isActive: true,
      createdAt: DateTime.now().subtract(const Duration(days: 365)),
    );
  }

  static List<Job> getDemoJobs() {
    final today = DateTime.now();
    return [
      Job(
        id: 'job_1',
        clientName: 'Sarah Johnson',
        clientPhone: '+1234567891',
        clientAddress: '123 Main St, Apt 4B, New York, NY 10001',
        serviceType: 'Deep Cleaning',
        scheduledDate: today,
        scheduledTime: '9:00 AM - 12:00 PM',
        price: 150.00,
        status: JobStatus.assigned,
        tasks: [
          Task(id: 'task_1', description: 'Clean kitchen'),
          Task(id: 'task_2', description: 'Clean bathrooms'),
          Task(id: 'task_3', description: 'Vacuum all rooms'),
          Task(id: 'task_4', description: 'Mop floors'),
        ],
        notes: 'Please use eco-friendly cleaning products. Pet-friendly home with 2 cats.',
      ),
      Job(
        id: 'job_2',
        clientName: 'Michael Chen',
        clientPhone: '+1234567892',
        clientAddress: '456 Oak Avenue, Brooklyn, NY 11201',
        serviceType: 'Standard Cleaning',
        scheduledDate: today,
        scheduledTime: '2:00 PM - 4:00 PM',
        price: 90.00,
        status: JobStatus.assigned,
        tasks: [
          Task(id: 'task_5', description: 'Dust all surfaces'),
          Task(id: 'task_6', description: 'Clean bathrooms'),
          Task(id: 'task_7', description: 'Vacuum'),
        ],
      ),
      Job(
        id: 'job_3',
        clientName: 'Emily Rodriguez',
        clientPhone: '+1234567893',
        clientAddress: '789 Park Lane, Manhattan, NY 10002',
        serviceType: 'Move-out Cleaning',
        scheduledDate: today.add(const Duration(days: 1)),
        scheduledTime: '10:00 AM - 3:00 PM',
        price: 250.00,
        status: JobStatus.assigned,
        tasks: [
          Task(id: 'task_8', description: 'Clean all rooms'),
          Task(id: 'task_9', description: 'Clean appliances'),
          Task(id: 'task_10', description: 'Clean windows'),
          Task(id: 'task_11', description: 'Deep clean bathrooms'),
        ],
        notes: 'Apartment is empty. Keys will be with building manager.',
      ),
      Job(
        id: 'job_4',
        clientName: 'David Kim',
        clientPhone: '+1234567894',
        clientAddress: '321 Elm Street, Queens, NY 11354',
        serviceType: 'Standard Cleaning',
        scheduledDate: today.subtract(const Duration(days: 1)),
        scheduledTime: '1:00 PM - 3:00 PM',
        price: 95.00,
        status: JobStatus.completed,
        tasks: [
          Task(id: 'task_12', description: 'General cleaning', isCompleted: true),
          Task(id: 'task_13', description: 'Kitchen cleaning', isCompleted: true),
          Task(id: 'task_14', description: 'Bathroom cleaning', isCompleted: true),
        ],
        clockInTime: today.subtract(const Duration(days: 1, hours: 11)),
        clockOutTime: today.subtract(const Duration(days: 1, hours: 9)),
      ),
    ];
  }

  static List<Payment> getDemoPayments() {
    final now = DateTime.now();
    return [
      Payment(
        id: 'payment_1',
        jobId: 'job_4',
        clientName: 'Job Earning - David Kim',
        amount: 95.00,
        status: PaymentStatus.completed,
        type: PaymentType.earnings,
        date: now.subtract(const Duration(days: 1)),
        transactionId: 'TXN_001',
      ),
      Payment(
        id: 'payment_2',
        jobId: 'job_5',
        clientName: 'Job Earning - Anna Williams',
        amount: 150.00,
        status: PaymentStatus.completed,
        type: PaymentType.earnings,
        date: now.subtract(const Duration(days: 3)),
        transactionId: 'TXN_002',
      ),
      Payment(
        id: 'payment_3',
        jobId: 'withdrawal_1',
        clientName: 'Bank Transfer',
        amount: 200.00,
        status: PaymentStatus.completed,
        type: PaymentType.withdrawal,
        date: now.subtract(const Duration(days: 5)),
        transactionId: 'TXN_003',
      ),
      Payment(
        id: 'payment_4',
        jobId: 'bonus_1',
        clientName: 'Performance Bonus',
        amount: 50.00,
        status: PaymentStatus.completed,
        type: PaymentType.bonus,
        date: now.subtract(const Duration(days: 7)),
        transactionId: 'TXN_004',
      ),
    ];
  }

  static Wallet getDemoWallet() {
    return Wallet(
      id: 'wallet_1',
      cleanerId: 'demo_cleaner_1',
      balance: 345.00,
      totalEarnings: 12750.00,
      totalWithdrawals: 12405.00,
      recentTransactions: getDemoPayments().take(3).toList(),
    );
  }
}

