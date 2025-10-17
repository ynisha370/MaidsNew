import React, { useState, useEffect } from 'react';
import { 
  Calendar, 
  Users, 
  DollarSign, 
  Package, 
  Settings,
  FileText,
  UserCheck,
  MessageSquare,
  BarChart3,
  Download,
  Plus,
  Edit,
  Trash2,
  Eye,
  CheckCircle,
  Clock,
  AlertCircle,
  CalendarDays,
  Receipt,
  LogOut,
  TrendingUp,
  Calendar as CalendarIcon,
  X,
  RotateCcw,
  Menu,
  Mail,
  Phone,
  XCircle
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';
import CalendarJobAssignment from './CalendarJobAssignment';
import DragDropTest from './DragDropTest';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import InvoiceManagement from './InvoiceManagement';
import PromoCodeManagement from './PromoCodeManagement';
import WaitlistManagement from './WaitlistManagement';
import CancellationManagement from './CancellationManagement';
import EmailReminders from './EmailReminders';
import SMSReminderManagement from './SMSReminderManagement';
import AdminSidebar from './AdminSidebar';
import CreateBookingForm from './CreateBookingForm';
import JobAssignmentManager from './JobAssignmentManager';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [stats, setStats] = useState({});
  const [bookings, setBookings] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [subscriptionFilter, setSubscriptionFilter] = useState('all');
  const [frequencyFilter, setFrequencyFilter] = useState('all');
  const [subscriptionSearch, setSubscriptionSearch] = useState('');
  const [cleaners, setCleaners] = useState([]);
  const [pendingCleaners, setPendingCleaners] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);

  // Form states
  const [newCleaner, setNewCleaner] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    google_calendar_credentials: null,
    calendar_integration_enabled: false
  });
  

  const [newService, setNewService] = useState({
    name: '',
    category: 'standard_cleaning',
    description: '',
    is_a_la_carte: false,
    a_la_carte_price: null,
    duration_hours: null
  });

  // Reports and Orders state
  const [weeklyStats, setWeeklyStats] = useState({
    totalBookings: 0,
    revenue: 0,
    cancellations: 0,
    reschedules: 0,
    completionRate: 0,
    customerSatisfaction: 0,
    avgBookingValue: 0,
    cleanerCompletions: [],
    totalCleanerCompletions: 0
  });
  const [monthlyStats, setMonthlyStats] = useState({
    totalBookings: 0,
    revenue: 0,
    cancellations: 0,
    reschedules: 0,
    completionRate: 0,
    customerSatisfaction: 0,
    avgBookingValue: 0,
    cleanerCompletions: [],
    totalCleanerCompletions: 0
  });
  const [pendingCancellations, setPendingCancellations] = useState([]);
  const [pendingReschedules, setPendingReschedules] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [showCreateBookingModal, setShowCreateBookingModal] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  // Computed filtered subscriptions
  const filteredSubscriptions = subscriptions.filter(subscription => {
    const matchesStatus = subscriptionFilter === 'all' || subscription.status === subscriptionFilter;
    const matchesFrequency = frequencyFilter === 'all' || subscription.frequency === frequencyFilter;
    const matchesSearch = subscriptionSearch === '' || 
      subscription.customer_id.toLowerCase().includes(subscriptionSearch.toLowerCase()) ||
      subscription.id.toLowerCase().includes(subscriptionSearch.toLowerCase());
    
    return matchesStatus && matchesFrequency && matchesSearch;
  });

  // Mobile menu data
  const mobileTabs = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3, shortcut: '1' },
    { id: 'bookings', label: 'Bookings', icon: Calendar, shortcut: '2', count: bookings.length },
    { id: 'subscriptions', label: 'Subscriptions', icon: Calendar, shortcut: '3', count: subscriptions.length },
    { id: 'customers', label: 'Customers', icon: Users, shortcut: '4' },
    { id: 'calendar', label: 'Calendar', icon: CalendarDays, shortcut: '5' },
    { id: 'dragtest', label: 'Drag Test', icon: CalendarDays, shortcut: 'Shift+3' },
    { id: 'invoices', label: 'Invoices', icon: Receipt, shortcut: '6' },
    { id: 'cleaners', label: 'Cleaners', icon: UserCheck, shortcut: '7', count: cleaners.length },
    { id: 'services', label: 'Services', icon: Package, shortcut: '8', count: services.length },
    { id: 'promos', label: 'Promo Codes', icon: DollarSign, shortcut: '9' },
    { id: 'reports', label: 'Reports', icon: TrendingUp, shortcut: '0' },
    { id: 'orders', label: 'Orders', icon: CalendarIcon, shortcut: 'Shift+1', count: pendingCancellations.length + pendingReschedules.length },
    { id: 'email-reminders', label: 'Email Reminders', icon: MessageSquare, shortcut: 'Shift+2' }
  ];

  // Handle tab change and close mobile menu
  const handleTabChange = (tabValue) => {
    setActiveTab(tabValue);
    setIsMobileMenuOpen(false);
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        loadStats(),
        loadBookings(),
        loadSubscriptions(),
        loadCleaners(),
        loadPendingCleaners(),
        loadServices(),
        loadCustomers()
      ]);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadBookings = async () => {
    try {
      const response = await axios.get(`${API}/admin/bookings`);
      setBookings(response.data);
    } catch (error) {
      console.error('Failed to load bookings:', error);
    }
  };

  const loadSubscriptions = async () => {
    try {
      const response = await axios.get(`${API}/admin/subscriptions`);
      setSubscriptions(response.data);
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
    }
  };

  const loadCleaners = async () => {
    try {
      const response = await axios.get(`${API}/admin/cleaners`);
      setCleaners(response.data);
    } catch (error) {
      console.error('Failed to load cleaners:', error);
    }
  };



  const loadServices = async () => {
    try {
      const response = await axios.get(`${API}/services`);
      setServices(response.data);
    } catch (error) {
      console.error('Failed to load services:', error);
    }
  };

  const loadCustomers = async () => {
    try {
      const response = await axios.get(`${API}/admin/customers`);
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    }
  };

  // Subscription management functions
  const pauseSubscription = async (subscriptionId) => {
    try {
      await axios.post(`${API}/admin/subscriptions/${subscriptionId}/pause`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Subscription paused successfully');
      loadSubscriptions();
    } catch (error) {
      console.error('Failed to pause subscription:', error);
      toast.error('Failed to pause subscription');
    }
  };

  const resumeSubscription = async (subscriptionId) => {
    try {
      await axios.post(`${API}/admin/subscriptions/${subscriptionId}/resume`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Subscription resumed successfully');
      loadSubscriptions();
    } catch (error) {
      console.error('Failed to resume subscription:', error);
      toast.error('Failed to resume subscription');
    }
  };

  const cancelSubscription = async (subscriptionId) => {
    try {
      await axios.post(`${API}/admin/subscriptions/${subscriptionId}/cancel`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Subscription cancelled successfully');
      loadSubscriptions();
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      toast.error('Failed to cancel subscription');
    }
  };

  const processSubscriptions = async () => {
    try {
      await axios.post(`${API}/admin/subscriptions/process`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      toast.success('Subscription processing completed');
      loadSubscriptions();
    } catch (error) {
      console.error('Failed to process subscriptions:', error);
      toast.error('Failed to process subscriptions');
    }
  };

  const exportSubscriptions = async () => {
    try {
      const response = await axios.get(`${API}/admin/subscriptions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      const csvData = response.data.map(subscription => ({
        'Subscription ID': subscription.id,
        'Customer ID': subscription.customer_id,
        'Frequency': subscription.frequency,
        'Status': subscription.status,
        'Next Booking Date': subscription.next_booking_date,
        'Preferred Time': subscription.preferred_time_slot,
        'Total Amount': subscription.total_amount,
        'Bookings Created': subscription.total_bookings_created,
        'Created At': subscription.created_at
      }));
      
      const csvContent = convertToCSV(csvData);
      downloadCSV(csvContent, 'subscriptions_export.csv');
      toast.success('Subscriptions exported successfully');
    } catch (error) {
      console.error('Failed to export subscriptions:', error);
      toast.error('Failed to export subscriptions');
    }
  };

  const viewSubscriptionDetails = async (subscriptionId) => {
    try {
      const response = await axios.get(`${API}/admin/subscriptions/${subscriptionId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      
      setSelectedSubscription(response.data);
      setShowSubscriptionModal(true);
    } catch (error) {
      console.error('Failed to get subscription details:', error);
      toast.error('Failed to get subscription details');
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast.success('Copied to clipboard');
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      toast.error('Failed to copy to clipboard');
    }
  };

  const convertToCSV = (data) => {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value;
        }).join(',')
      )
    ];
    
    return csvRows.join('\n');
  };

  const downloadCSV = (csvContent, filename) => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Customer management functions
  const createBookingForCustomer = async (bookingData) => {
    try {
      await axios.post(`${API}/admin/bookings`, bookingData);
      toast.success('Booking created successfully');
      setShowCreateBookingModal(false);
      setSelectedCustomer(null);
      loadBookings();
    } catch (error) {
      toast.error('Failed to create booking');
      console.error(error);
    }
  };

  const handleCreateBooking = (customer) => {
    setSelectedCustomer(customer);
    setShowCreateBookingModal(true);
  };

  // Booking management functions
  const updateBookingStatus = async (bookingId, status) => {
    try {
      await axios.patch(`${API}/admin/bookings/${bookingId}`, { status });
      toast.success('Booking status updated');
      loadBookings();
    } catch (error) {
      toast.error('Failed to update booking status');
    }
  };

  const assignCleaner = async (bookingId, cleanerId) => {
    try {
      await axios.patch(`${API}/admin/bookings/${bookingId}`, { cleaner_id: cleanerId });
      toast.success('Cleaner assigned successfully');
      loadBookings();
    } catch (error) {
      toast.error('Failed to assign cleaner');
    }
  };

  // Cleaner management functions
  const createCleaner = async () => {
    try {
      await axios.post(`${API}/admin/cleaners`, newCleaner);
      toast.success('Cleaner created successfully');
      setNewCleaner({ 
        email: '', 
        first_name: '', 
        last_name: '', 
        phone: '',
        google_calendar_credentials: null,
        calendar_integration_enabled: false
      });
      loadCleaners();
    } catch (error) {
      toast.error('Failed to create cleaner');
    }
  };

  const deleteCleaner = async (cleanerId) => {
    try {
      await axios.delete(`${API}/admin/cleaners/${cleanerId}`);
      toast.success('Cleaner deleted successfully');
      loadCleaners();
    } catch (error) {
      toast.error('Failed to delete cleaner');
    }
  };

  // Pending cleaners management functions
  const loadPendingCleaners = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/cleaners/pending`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPendingCleaners(response.data.pending_cleaners || []);
    } catch (error) {
      console.error('Failed to load pending cleaners:', error);
      toast.error('Failed to load pending cleaners');
    }
  };

  const approveCleaner = async (cleanerId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/admin/cleaners/${cleanerId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success(response.data.message || 'Cleaner approved successfully');
      loadPendingCleaners();
      loadCleaners();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to approve cleaner');
    }
  };

  const rejectCleaner = async (cleanerId, reason = '') => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API}/admin/cleaners/${cleanerId}/reject?reason=${encodeURIComponent(reason)}`, 
        {}, 
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      toast.success('Cleaner application rejected');
      loadPendingCleaners();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reject cleaner');
    }
  };


  // Service management functions
  const createService = async () => {
    try {
      // Prepare service data with proper is_a_la_carte flag
      const serviceData = {
        ...newService,
        is_a_la_carte: newService.category === 'a_la_carte'
      };
      
      await axios.post(`${API}/admin/services`, serviceData);
      toast.success('Service created successfully');
      setNewService({
        name: '',
        category: 'standard_cleaning',
        description: '',
        is_a_la_carte: false,
        a_la_carte_price: null,
        duration_hours: null
      });
      loadServices();
    } catch (error) {
      toast.error('Failed to create service');
    }
  };

  const deleteService = async (serviceId) => {
    try {
      await axios.delete(`${API}/admin/services/${serviceId}`);
      toast.success('Service deleted successfully');
      loadServices();
    } catch (error) {
      toast.error('Failed to delete service');
    }
  };


  // Export function
  const exportBookings = async () => {
    try {
      const response = await axios.get(`${API}/admin/export/bookings`);
      const csvData = response.data.data;
      
      // Convert to CSV
      const headers = Object.keys(csvData[0] || {});
      const csvContent = [
        headers.join(','),
        ...csvData.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n');

      // Download file
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.data.filename;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast.success('Bookings exported successfully');
    } catch (error) {
      toast.error('Failed to export bookings');
    }
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={`${statusColors[status] || 'bg-gray-100 text-gray-800'} border-0`}>
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </Badge>
    );
  };

  const getPriorityBadge = (priority) => {
    const priorityColors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={`${priorityColors[priority] || 'bg-gray-100 text-gray-800'} border-0`}>
        {priority?.charAt(0).toUpperCase() + priority?.slice(1)}
      </Badge>
    );
  };

  // Reports and Orders functions
  const loadReports = async () => {
    try {
      const [weeklyResponse, monthlyResponse] = await Promise.all([
        axios.get(`${API}/admin/reports/weekly`),
        axios.get(`${API}/admin/reports/monthly`)
      ]);
      
      setWeeklyStats(weeklyResponse.data);
      setMonthlyStats(monthlyResponse.data);
    } catch (error) {
      console.error('Failed to load reports:', error);
      toast.error('Failed to load reports');
    }
  };

  const loadPendingOrders = async () => {
    try {
      const response = await axios.get(`${API}/admin/orders/pending`);
      setPendingCancellations(response.data.cancellations || []);
      setPendingReschedules(response.data.reschedules || []);
    } catch (error) {
      console.error('Failed to load pending orders:', error);
      toast.error('Failed to load pending orders');
    }
  };

  const loadOrderHistory = async () => {
    try {
      const response = await axios.get(`${API}/admin/orders/history`);
      setOrderHistory(response.data || []);
    } catch (error) {
      console.error('Failed to load order history:', error);
      toast.error('Failed to load order history');
    }
  };

  const handleOrderAction = async (orderId, action) => {
    try {
      await axios.post(`${API}/admin/orders/${orderId}/${action}`);
      toast.success(`Order ${action.replace('_', ' ')} successful`);
      loadPendingOrders();
      loadOrderHistory();
    } catch (error) {
      console.error(`Failed to ${action}:`, error);
      toast.error(`Failed to ${action.replace('_', ' ')} order`);
    }
  };

  const exportReport = async (type) => {
    try {
      const response = await axios.get(`${API}/admin/reports/${type}/export`);
      const csvData = response.data.data;
      
      // Convert to CSV
      const headers = Object.keys(csvData[0] || {});
      const csvContent = [
        headers.join(','),
        ...csvData.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n');
      
      // Download CSV
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${type}_report_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
      
      toast.success(`${type.charAt(0).toUpperCase() + type.slice(1)} report exported`);
    } catch (error) {
      console.error(`Failed to export ${type} report:`, error);
      toast.error(`Failed to export ${type} report`);
    }
  };

  // Load reports and orders when switching to those tabs
  useEffect(() => {
    if (activeTab === 'reports') {
      loadReports();
    } else if (activeTab === 'orders') {
      loadPendingOrders();
      loadOrderHistory();
    }
  }, [activeTab]);

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.ctrlKey || event.metaKey) {
        const tabOrder = [
          'dashboard', 'bookings', 'calendar', 'invoices', 'cleaners', 
          'services', 'promos', 'reports', 'orders'
        ];
        const currentIndex = tabOrder.indexOf(activeTab);
        
        if (event.key === 'ArrowLeft' && currentIndex > 0) {
          event.preventDefault();
          handleTabChange(tabOrder[currentIndex - 1]);
        } else if (event.key === 'ArrowRight' && currentIndex < tabOrder.length - 1) {
          event.preventDefault();
          handleTabChange(tabOrder[currentIndex + 1]);
        } else if (event.key >= '1' && event.key <= '9') {
          event.preventDefault();
          const tabIndex = parseInt(event.key) - 1;
          if (tabIndex < tabOrder.length) {
            handleTabChange(tabOrder[tabIndex]);
          }
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [activeTab]);

  // Close mobile menu on window resize to desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">

      {/* New Sidebar Layout */}
      <div className="flex h-screen">
        {/* Sidebar */}
        <AdminSidebar
          activeTab={activeTab}
          onTabChange={handleTabChange}
          isCollapsed={isSidebarCollapsed}
          onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
          stats={stats}
          counts={{
            subscriptions: subscriptions.length,
            cleaners: cleaners.length,
            services: services.length,
            orders: pendingCancellations.length + pendingReschedules.length,
          }}
          onLogout={() => {
            logout();
            navigate('/admin/login');
          }}
        />

        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'ml-16' : 'ml-72'}`}>
          <div className="h-full overflow-y-auto bg-gray-50">
            <div className="p-6">
              <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-6">
                <style jsx>{`
                  .tab-content {
                    animation: fadeIn 0.3s ease-in-out;
                  }
                  @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                  }
                `}</style>

          {/* Dashboard Overview */}
          <TabsContent value="dashboard" className="space-y-6 tab-content">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Bookings</p>
                      <p className="text-2xl font-bold">{stats.total_bookings || 0}</p>
                    </div>
                    <Calendar className="text-blue-600" size={24} />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Total Revenue</p>
                      <p className="text-2xl font-bold">${(stats.total_revenue || 0).toFixed(2)}</p>
                    </div>
                    <DollarSign className="text-green-600" size={24} />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Active Cleaners</p>
                      <p className="text-2xl font-bold">{stats.total_cleaners || 0}</p>
                    </div>
                    <Users className="text-purple-600" size={24} />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                    </div>
                    <MessageSquare className="text-orange-600" size={24} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Bookings */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Bookings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {bookings.slice(0, 5).map((booking) => (
                    <div key={booking.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">Booking #{booking.id.slice(-8)}</p>
                        <p className="text-sm text-gray-600">{booking.booking_date} at {booking.time_slot}</p>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(booking.status)}
                        <p className="text-sm font-medium mt-1">${booking.total_amount}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Cleaner Performance Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UserCheck className="mr-2" size={20} />
                  Cleaner Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {weeklyStats.totalCleanerCompletions || 0}
                    </div>
                    <div className="text-sm text-gray-600">Jobs Completed This Week</div>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {weeklyStats.cleanerCompletions ? weeklyStats.cleanerCompletions.length : 0}
                    </div>
                    <div className="text-sm text-gray-600">Active Cleaners</div>
                  </div>
                </div>
                
                {weeklyStats.cleanerCompletions && weeklyStats.cleanerCompletions.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">Top Performers</h4>
                    <div className="space-y-2">
                      {weeklyStats.cleanerCompletions
                        .sort((a, b) => b.jobs_completed - a.jobs_completed)
                        .slice(0, 3)
                        .map((cleaner, index) => (
                        <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                          <span className="text-sm font-medium">{cleaner.cleaner_name}</span>
                          <div className="text-right">
                            <span className="text-sm font-semibold text-green-600">
                              {cleaner.jobs_completed} jobs
                            </span>
                            <span className="text-xs text-gray-500 ml-2">
                              ${cleaner.total_revenue.toFixed(2)}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Calendar Job Assignment */}
          <TabsContent value="calendar" className="space-y-6 tab-content">
            <CalendarJobAssignment />
          </TabsContent>

          {/* Drag Drop Test */}
          <TabsContent value="dragtest" className="space-y-6 tab-content">
            <DragDropTest />
          </TabsContent>

          {/* Invoice Management */}
          <TabsContent value="invoices" className="space-y-6 tab-content">
            <InvoiceManagement />
          </TabsContent>

          {/* Promo Code Management */}
          <TabsContent value="promos" className="space-y-6 tab-content">
            <PromoCodeManagement />
          </TabsContent>

          {/* Reports */}
          <TabsContent value="reports" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Reports & Analytics</h2>
              <div className="flex space-x-2">
                <Button onClick={() => exportReport('weekly')} variant="outline">
                  <Download className="mr-2" size={16} />
                  Weekly Report
                </Button>
                <Button onClick={() => exportReport('monthly')} variant="outline">
                  <Download className="mr-2" size={16} />
                  Monthly Report
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Weekly Report */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="mr-2" size={20} />
                    Weekly Report
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Total Bookings:</span>
                      <span className="font-semibold">{weeklyStats.totalBookings}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Revenue:</span>
                      <span className="font-semibold text-green-600">${weeklyStats.revenue}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Cancellations:</span>
                      <span className="font-semibold text-red-600">{weeklyStats.cancellations}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Reschedules:</span>
                      <span className="font-semibold text-yellow-600">{weeklyStats.reschedules}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Monthly Report */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <BarChart3 className="mr-2" size={20} />
                    Monthly Report
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Total Bookings:</span>
                      <span className="font-semibold">{monthlyStats.totalBookings}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Revenue:</span>
                      <span className="font-semibold text-green-600">${monthlyStats.revenue}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Cancellations:</span>
                      <span className="font-semibold text-red-600">{monthlyStats.cancellations}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Reschedules:</span>
                      <span className="font-semibold text-yellow-600">{monthlyStats.reschedules}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Analytics */}
            <Card>
              <CardHeader>
                <CardTitle>Detailed Analytics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{weeklyStats.completionRate}%</div>
                    <div className="text-sm text-gray-600">Completion Rate</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{weeklyStats.customerSatisfaction}%</div>
                    <div className="text-sm text-gray-600">Customer Satisfaction</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{weeklyStats.avgBookingValue}</div>
                    <div className="text-sm text-gray-600">Avg Booking Value</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Cleaner Job Completions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UserCheck className="mr-2" size={20} />
                  Cleaner Job Completions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Cleaner Completions:</span>
                    <span className="font-semibold text-green-600">{weeklyStats.totalCleanerCompletions || 0}</span>
                  </div>
                  
                  {weeklyStats.cleanerCompletions && weeklyStats.cleanerCompletions.length > 0 ? (
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-800">Completions by Cleaner</h4>
                      {weeklyStats.cleanerCompletions.map((cleaner, index) => (
                        <div key={index} className="p-3 border rounded-lg bg-gray-50">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h5 className="font-medium">{cleaner.cleaner_name}</h5>
                              <p className="text-sm text-gray-600">
                                {cleaner.jobs_completed} job{cleaner.jobs_completed !== 1 ? 's' : ''} completed
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-green-600">${cleaner.total_revenue.toFixed(2)}</p>
                              <p className="text-sm text-gray-600">Revenue</p>
                            </div>
                          </div>
                          
                          {cleaner.completions && cleaner.completions.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {cleaner.completions.slice(0, 3).map((completion, compIndex) => (
                                <div key={compIndex} className="text-xs text-gray-600 flex justify-between">
                                  <span>Job #{completion.job_id.slice(-8)}</span>
                                  <span>${completion.total_amount.toFixed(2)}</span>
                                </div>
                              ))}
                              {cleaner.completions.length > 3 && (
                                <p className="text-xs text-gray-500">
                                  +{cleaner.completions.length - 3} more job{cleaner.completions.length - 3 !== 1 ? 's' : ''}
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">No cleaner completions this week</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Order Management */}
          <TabsContent value="orders" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Order Management</h2>
              <div className="flex space-x-2">
                <Button onClick={loadPendingOrders} variant="outline">
                  <RotateCcw className="mr-2" size={16} />
                  Refresh
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Pending Cancellations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <X className="mr-2 text-red-600" size={20} />
                    Pending Cancellations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {pendingCancellations.map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">#{order.id.slice(-8)}</div>
                          <div className="text-sm text-gray-600">{order.customer_name}</div>
                          <div className="text-sm text-gray-500">{order.booking_date}</div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleOrderAction(order.id, 'approve_cancellation')}
                          >
                            Approve
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleOrderAction(order.id, 'deny_cancellation')}
                          >
                            Deny
                          </Button>
                        </div>
                      </div>
                    ))}
                    {pendingCancellations.length === 0 && (
                      <p className="text-gray-500 text-center py-4">No pending cancellations</p>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Pending Reschedules */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <RotateCcw className="mr-2 text-yellow-600" size={20} />
                    Pending Reschedules
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {pendingReschedules.map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">#{order.id.slice(-8)}</div>
                          <div className="text-sm text-gray-600">{order.customer_name}</div>
                          <div className="text-sm text-gray-500">
                            {order.original_date} → {order.new_date}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleOrderAction(order.id, 'approve_reschedule')}
                          >
                            Approve
                          </Button>
                          <Button 
                            size="sm" 
                            variant="destructive"
                            onClick={() => handleOrderAction(order.id, 'deny_reschedule')}
                          >
                            Deny
                          </Button>
                        </div>
                      </div>
                    ))}
                    {pendingReschedules.length === 0 && (
                      <p className="text-gray-500 text-center py-4">No pending reschedules</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Order History */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Order Changes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {orderHistory.map((order) => (
                    <div key={order.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          order.type === 'cancellation' ? 'bg-red-500' : 'bg-yellow-500'
                        }`}></div>
                        <div>
                          <div className="font-medium">#{order.id.slice(-8)}</div>
                          <div className="text-sm text-gray-600">{order.customer_name}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">
                          {order.type === 'cancellation' ? 'Cancelled' : 'Rescheduled'}
                        </div>
                        <div className="text-xs text-gray-500">{order.timestamp}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Bookings Management */}
          <TabsContent value="bookings" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Booking Management</h2>
              <Button onClick={exportBookings} className="btn-hover">
                <Download className="mr-2" size={16} />
                Export CSV
              </Button>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b">
                      <tr>
                        <th className="text-left p-4">Booking ID</th>
                        <th className="text-left p-4">Customer</th>
                        <th className="text-left p-4">Date & Time</th>
                        <th className="text-left p-4">Services</th>
                        <th className="text-left p-4">Amount</th>
                        <th className="text-left p-4">Status</th>
                        <th className="text-left p-4">Cleaner</th>
                        <th className="text-left p-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bookings.map((booking) => (
                        <tr key={booking.id} className="border-b">
                          <td className="p-4">#{booking.id.slice(-8)}</td>
                          <td className="p-4">{booking.customer_id.slice(-8)}</td>
                          <td className="p-4">
                            <div>
                              <p>{booking.booking_date}</p>
                              <p className="text-sm text-gray-600">{booking.time_slot}</p>
                            </div>
                          </td>
                          <td className="p-4">{booking.house_size} • {booking.frequency}</td>
                          <td className="p-4 font-medium">${booking.total_amount}</td>
                          <td className="p-4">{getStatusBadge(booking.status)}</td>
                          <td className="p-4">
                            <Select
                              value={booking.cleaner_id || undefined}
                              onValueChange={(value) => assignCleaner(booking.id, value === 'none' ? null : value)}
                            >
                              <SelectTrigger className="w-32">
                                <SelectValue placeholder="Assign" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="none">Unassigned</SelectItem>
                                {cleaners.map((cleaner) => (
                                  <SelectItem key={cleaner.id} value={cleaner.id}>
                                    {cleaner.first_name} {cleaner.last_name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </td>
                          <td className="p-4">
                            <div className="flex space-x-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateBookingStatus(booking.id, 'confirmed')}
                                disabled={booking.status === 'confirmed'}
                              >
                                <CheckCircle size={14} />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateBookingStatus(booking.id, 'completed')}
                                disabled={booking.status === 'completed'}
                              >
                                Complete
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscriptions Management */}
          <TabsContent value="subscriptions" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Subscription Management</h2>
              <div className="flex space-x-2">
                <Button onClick={processSubscriptions} className="btn-hover">
                  <RotateCcw className="mr-2" size={16} />
                  Process Subscriptions
                </Button>
                <Button onClick={exportSubscriptions} className="btn-hover">
                  <Download className="mr-2" size={16} />
                  Export CSV
                </Button>
              </div>
            </div>

            {/* Subscription Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Subscriptions</p>
                      <p className="text-2xl font-bold">{subscriptions.length}</p>
                    </div>
                    <Calendar className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Active</p>
                      <p className="text-2xl font-bold text-green-600">
                        {subscriptions.filter(s => s.status === 'active').length}
                      </p>
                    </div>
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Paused</p>
                      <p className="text-2xl font-bold text-yellow-600">
                        {subscriptions.filter(s => s.status === 'paused').length}
                      </p>
                    </div>
                    <Clock className="h-8 w-8 text-yellow-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Cancelled</p>
                      <p className="text-2xl font-bold text-red-600">
                        {subscriptions.filter(s => s.status === 'cancelled').length}
                      </p>
                    </div>
                    <XCircle className="h-8 w-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Subscription Filters */}
            <Card>
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-4 items-center">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium">Filter by Status:</label>
                    <Select onValueChange={(value) => setSubscriptionFilter(value)}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="paused">Paused</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium">Filter by Frequency:</label>
                    <Select onValueChange={(value) => setFrequencyFilter(value)}>
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="All Frequencies" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Frequencies</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="bi_weekly">Bi-weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                        <SelectItem value="every_3_weeks">Every 3 Weeks</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Input
                      placeholder="Search by customer ID..."
                      value={subscriptionSearch}
                      onChange={(e) => setSubscriptionSearch(e.target.value)}
                      className="w-48"
                    />
                  </div>
                  
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSubscriptionFilter('all');
                      setFrequencyFilter('all');
                      setSubscriptionSearch('');
                    }}
                  >
                    Clear Filters
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Subscriptions Table */}
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="border-b bg-gray-50">
                      <tr>
                        <th className="text-left p-4 font-medium">Subscription ID</th>
                        <th className="text-left p-4 font-medium">Customer</th>
                        <th className="text-left p-4 font-medium">Frequency</th>
                        <th className="text-left p-4 font-medium">Next Booking</th>
                        <th className="text-left p-4 font-medium">Total Amount</th>
                        <th className="text-left p-4 font-medium">Status</th>
                        <th className="text-left p-4 font-medium">Progress</th>
                        <th className="text-left p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSubscriptions.map((subscription) => (
                        <tr key={subscription.id} className="border-b hover:bg-gray-50">
                          <td className="p-4">
                            <div className="flex items-center space-x-2">
                              <span className="font-mono text-sm">#{subscription.id.slice(-8)}</span>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => copyToClipboard(subscription.id)}
                              >
                                <Eye size={14} />
                              </Button>
                            </div>
                          </td>
                          <td className="p-4">
                            <div>
                              <p className="font-medium">{subscription.customer_id.slice(-8)}</p>
                              <p className="text-sm text-gray-600">ID: {subscription.customer_id}</p>
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline" className="capitalize">
                              {subscription.frequency.replace('_', ' ')}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <div>
                              <p className="font-medium">{subscription.next_booking_date}</p>
                              <p className="text-sm text-gray-600">{subscription.preferred_time_slot}</p>
                            </div>
                          </td>
                          <td className="p-4">
                            <div>
                              <p className="font-medium">${subscription.total_amount}</p>
                              <p className="text-sm text-gray-600">per booking</p>
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge 
                              variant={
                                subscription.status === 'active' ? 'default' :
                                subscription.status === 'paused' ? 'secondary' :
                                subscription.status === 'cancelled' ? 'destructive' : 'outline'
                              }
                            >
                              {subscription.status.toUpperCase()}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <div className="flex items-center space-x-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full" 
                                  style={{ 
                                    width: `${Math.min(100, (subscription.total_bookings_created / 12) * 100)}%` 
                                  }}
                                ></div>
                              </div>
                              <span className="text-sm text-gray-600">
                                {subscription.total_bookings_created}/12
                              </span>
                            </div>
                          </td>
                          <td className="p-4">
                            <div className="flex space-x-2">
                              {subscription.status === 'active' ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => pauseSubscription(subscription.id)}
                                  title="Pause Subscription"
                                >
                                  <Clock size={14} />
                                </Button>
                              ) : subscription.status === 'paused' ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => resumeSubscription(subscription.id)}
                                  title="Resume Subscription"
                                >
                                  <CheckCircle size={14} />
                                </Button>
                              ) : null}
                              
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => viewSubscriptionDetails(subscription.id)}
                                title="View Details"
                              >
                                <Eye size={14} />
                              </Button>
                              
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => cancelSubscription(subscription.id)}
                                className="text-red-600 hover:text-red-700"
                                title="Cancel Subscription"
                              >
                                <XCircle size={14} />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  
                  {filteredSubscriptions.length === 0 && (
                    <div className="text-center py-8">
                      <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No subscriptions found</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {subscriptions.length === 0 
                          ? "Subscriptions will appear here when customers create recurring bookings."
                          : "Try adjusting your filters to see more results."
                        }
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Customer Management */}
          <TabsContent value="customers" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Customer Management</h2>
              <Badge variant="outline">{customers.length} customers</Badge>
            </div>

            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {customers.length === 0 ? (
                    <div className="text-center py-8">
                      <Users className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No customers found</h3>
                      <p className="mt-1 text-sm text-gray-500">Customers will appear here once they sign up or make bookings.</p>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Address</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {customers.map((customer) => (
                            <tr key={customer.id} className="hover:bg-gray-50">
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                  <div className="flex-shrink-0 h-10 w-10">
                                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                                      <span className="text-sm font-medium text-blue-600">
                                        {customer.first_name?.charAt(0)}{customer.last_name?.charAt(0)}
                                      </span>
                                    </div>
                                  </div>
                                  <div className="ml-4">
                                    <div className="text-sm font-medium text-gray-900">
                                      {customer.first_name} {customer.last_name}
                                    </div>
                                    <div className="text-sm text-gray-500">ID: {customer.id}</div>
                                  </div>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">{customer.email}</div>
                                {customer.phone && (
                                  <div className="text-sm text-gray-500">{customer.phone}</div>
                                )}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-900">
                                  {customer.address && `${customer.address}, `}
                                  {customer.city && `${customer.city}, `}
                                  {customer.state && `${customer.state} `}
                                  {customer.zip_code}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <Badge variant={customer.is_guest ? "secondary" : "default"}>
                                  {customer.is_guest ? "Guest" : "Registered"}
                                </Badge>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <div className="flex space-x-2">
                                  <Button
                                    size="sm"
                                    onClick={() => handleCreateBooking(customer)}
                                    className="bg-blue-600 hover:bg-blue-700"
                                  >
                                    <Plus className="h-4 w-4 mr-1" />
                                    Create Booking
                                  </Button>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => {
                                      // View customer details
                                      setSelectedCustomer(customer);
                                    }}
                                  >
                                    <Eye className="h-4 w-4" />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Cleaners Management */}
          <TabsContent value="cleaners" className="space-y-6 tab-content">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Cleaner Management</h2>
            </div>

            <Tabs defaultValue="approved" className="w-full">
              <TabsList className="grid w-full grid-cols-2 mb-6">
                <TabsTrigger value="approved">
                  All Cleaners ({cleaners.length})
                </TabsTrigger>
                <TabsTrigger value="pending">
                  Pending Approval 
                  {pendingCleaners.length > 0 && (
                    <Badge className="ml-2 bg-orange-500">{pendingCleaners.length}</Badge>
                  )}
                </TabsTrigger>
              </TabsList>

              <TabsContent value="approved" className="space-y-4">
                <div className="flex justify-end mb-4">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button className="btn-hover">
                        <Plus className="mr-2" size={16} />
                        Add Cleaner
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add New Cleaner</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <Input
                            placeholder="First Name"
                            value={newCleaner.first_name}
                            onChange={(e) => setNewCleaner({...newCleaner, first_name: e.target.value})}
                          />
                          <Input
                            placeholder="Last Name"
                            value={newCleaner.last_name}
                            onChange={(e) => setNewCleaner({...newCleaner, last_name: e.target.value})}
                          />
                        </div>
                        <Input
                          placeholder="Email"
                          type="email"
                          value={newCleaner.email}
                          onChange={(e) => setNewCleaner({...newCleaner, email: e.target.value})}
                        />
                        <Input
                          placeholder="Phone"
                          value={newCleaner.phone}
                          onChange={(e) => setNewCleaner({...newCleaner, phone: e.target.value})}
                        />
                        <Button onClick={createCleaner} className="w-full">
                          Create Cleaner
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {cleaners.map((cleaner) => (
                    <Card key={cleaner.id}>
                      <CardContent className="p-6">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="font-semibold">{cleaner.first_name} {cleaner.last_name}</h3>
                            <p className="text-sm text-gray-600">{cleaner.email}</p>
                            <p className="text-sm text-gray-600">{cleaner.phone}</p>
                          </div>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteCleaner(cleaner.id)}
                          >
                            <Trash2 size={14} />
                          </Button>
                        </div>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm">Total Jobs:</span>
                            <span className="font-medium">{cleaner.total_jobs}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Rating:</span>
                            <span className="font-medium">{cleaner.rating.toFixed(1)}/5.0</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm">Status:</span>
                            <Badge className={cleaner.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                              {cleaner.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="pending" className="space-y-4">
                {pendingCleaners.length === 0 ? (
                  <Card>
                    <CardContent className="p-12 text-center">
                      <UserCheck className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Applications</h3>
                      <p className="text-gray-500">There are no cleaner applications awaiting approval.</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 gap-4">
                    {pendingCleaners.map((cleaner) => (
                      <Card key={cleaner.id} className="border-orange-200 bg-orange-50/30">
                        <CardContent className="p-6">
                          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <h3 className="font-semibold text-lg">
                                  {cleaner.first_name} {cleaner.last_name}
                                </h3>
                                <Badge className="bg-orange-500">Pending</Badge>
                              </div>
                              <div className="space-y-1 text-sm text-gray-600">
                                <p className="flex items-center gap-2">
                                  <Mail size={14} />
                                  {cleaner.email}
                                </p>
                                <p className="flex items-center gap-2">
                                  <Phone size={14} />
                                  {cleaner.phone}
                                </p>
                                <p className="flex items-center gap-2">
                                  <Clock size={14} />
                                  Applied: {new Date(cleaner.created_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Dialog>
                                <DialogTrigger asChild>
                                  <Button size="sm" variant="outline" className="text-gray-600">
                                    <Eye className="mr-1" size={14} />
                                    View Details
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>Cleaner Application Details</DialogTitle>
                                  </DialogHeader>
                                  <div className="space-y-4">
                                    <div>
                                      <h4 className="font-medium mb-2">Personal Information</h4>
                                      <div className="space-y-2 text-sm">
                                        <p><strong>Name:</strong> {cleaner.first_name} {cleaner.last_name}</p>
                                        <p><strong>Email:</strong> {cleaner.email}</p>
                                        <p><strong>Phone:</strong> {cleaner.phone}</p>
                                        <p><strong>Applied:</strong> {new Date(cleaner.created_at).toLocaleString()}</p>
                                      </div>
                                    </div>
                                  </div>
                                </DialogContent>
                              </Dialog>
                              <Button 
                                size="sm" 
                                className="bg-green-600 hover:bg-green-700"
                                onClick={() => {
                                  if (window.confirm(`Approve ${cleaner.first_name} ${cleaner.last_name}?`)) {
                                    approveCleaner(cleaner.id);
                                  }
                                }}
                              >
                                <CheckCircle className="mr-1" size={14} />
                                Approve
                              </Button>
                              <Button 
                                size="sm" 
                                variant="destructive"
                                onClick={() => {
                                  const reason = prompt(`Reject ${cleaner.first_name} ${cleaner.last_name}?\n\nOptional: Enter rejection reason:`);
                                  if (reason !== null) {
                                    rejectCleaner(cleaner.id, reason);
                                  }
                                }}
                              >
                                <XCircle className="mr-1" size={14} />
                                Reject
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </TabsContent>

          {/* Services Management */}
          <TabsContent value="services" className="space-y-6 tab-content">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Service Management</h2>
              <Dialog>
                <DialogTrigger asChild>
                  <Button className="btn-hover">
                    <Plus className="mr-2" size={16} />
                    Add Service
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Add New Service</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4">
                    <Input
                      placeholder="Service Name"
                      value={newService.name}
                      onChange={(e) => setNewService({...newService, name: e.target.value})}
                    />
                    <Select
                      value={newService.category}
                      onValueChange={(value) => setNewService({
                        ...newService, 
                        category: value,
                        is_a_la_carte: value === 'a_la_carte'
                      })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select Category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="standard_cleaning">Standard Cleaning</SelectItem>
                        <SelectItem value="a_la_carte">A La Carte</SelectItem>
                      </SelectContent>
                    </Select>
                    <Textarea
                      placeholder="Description"
                      value={newService.description}
                      onChange={(e) => setNewService({...newService, description: e.target.value})}
                    />
                    {newService.category === 'a_la_carte' && (
                      <Input
                        placeholder="Price"
                        type="number"
                        value={newService.a_la_carte_price || ''}
                        onChange={(e) => setNewService({...newService, a_la_carte_price: parseFloat(e.target.value)})}
                      />
                    )}
                    {newService.category === 'standard_cleaning' && (
                      <Input
                        placeholder="Duration (hours)"
                        type="number"
                        value={newService.duration_hours || ''}
                        onChange={(e) => setNewService({...newService, duration_hours: parseInt(e.target.value)})}
                      />
                    )}
                    <Button onClick={createService} className="w-full">
                      Create Service
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {services.map((service) => (
                <Card key={service.id}>
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-semibold">{service.name}</h3>
                        <Badge className="mt-1">
                          {service.is_a_la_carte ? 'A La Carte' : 'Standard'}
                        </Badge>
                      </div>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => deleteService(service.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{service.description}</p>
                    <div className="space-y-1 text-sm">
                      {service.is_a_la_carte && service.a_la_carte_price && (
                        <p><strong>Price:</strong> ${service.a_la_carte_price}</p>
                      )}
                      {service.duration_hours && (
                        <p><strong>Duration:</strong> {service.duration_hours} hours</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>



          <TabsContent value="waitlist" className="space-y-6 tab-content">
            <WaitlistManagement />
          </TabsContent>
          <TabsContent value="cancellations" className="space-y-6 tab-content">
            <CancellationManagement />
          </TabsContent>
          <TabsContent value="email-reminders" className="space-y-6 tab-content">
            <EmailReminders />
          </TabsContent>
          <TabsContent value="sms-reminders" className="space-y-6 tab-content">
            <SMSReminderManagement />
          </TabsContent>
              </Tabs>
            </div>
          </div>
        </div>
      </div>

      {/* Create Booking Modal */}
      <Dialog open={showCreateBookingModal} onOpenChange={setShowCreateBookingModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create Booking for {selectedCustomer?.first_name} {selectedCustomer?.last_name}</DialogTitle>
          </DialogHeader>
          {selectedCustomer && (
            <CreateBookingForm
              customer={selectedCustomer}
              services={services}
              onSubmit={createBookingForCustomer}
              onCancel={() => setShowCreateBookingModal(false)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Subscription Details Modal */}
      <Dialog open={showSubscriptionModal} onOpenChange={setShowSubscriptionModal}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Subscription Details</DialogTitle>
          </DialogHeader>
          {selectedSubscription && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Subscription ID</label>
                  <p className="font-mono text-sm">{selectedSubscription.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Status</label>
                  <Badge 
                    variant={
                      selectedSubscription.status === 'active' ? 'default' :
                      selectedSubscription.status === 'paused' ? 'secondary' :
                      selectedSubscription.status === 'cancelled' ? 'destructive' : 'outline'
                    }
                  >
                    {selectedSubscription.status.toUpperCase()}
                  </Badge>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Customer ID</label>
                  <p className="font-mono text-sm">{selectedSubscription.customer_id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Frequency</label>
                  <Badge variant="outline" className="capitalize">
                    {selectedSubscription.frequency.replace('_', ' ')}
                  </Badge>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Next Booking Date</label>
                  <p className="text-sm">{selectedSubscription.next_booking_date}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Preferred Time Slot</label>
                  <p className="text-sm">{selectedSubscription.preferred_time_slot}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Total Amount</label>
                  <p className="text-lg font-semibold">${selectedSubscription.total_amount}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Bookings Created</label>
                  <p className="text-sm">{selectedSubscription.total_bookings_created} / 12</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-600">Start Date</label>
                  <p className="text-sm">{selectedSubscription.start_date}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-600">Created At</label>
                  <p className="text-sm">{new Date(selectedSubscription.created_at).toLocaleString()}</p>
                </div>
              </div>
              
              {selectedSubscription.address && (
                <div>
                  <label className="text-sm font-medium text-gray-600">Address</label>
                  <p className="text-sm">
                    {selectedSubscription.address.street}, {selectedSubscription.address.city}, 
                    {selectedSubscription.address.state} {selectedSubscription.address.zip_code}
                  </p>
                </div>
              )}
              
              {selectedSubscription.special_instructions && (
                <div>
                  <label className="text-sm font-medium text-gray-600">Special Instructions</label>
                  <p className="text-sm">{selectedSubscription.special_instructions}</p>
                </div>
              )}
              
              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setShowSubscriptionModal(false)}
                >
                  Close
                </Button>
                <Button
                  onClick={() => {
                    copyToClipboard(selectedSubscription.id);
                  }}
                >
                  Copy ID
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AdminDashboard;