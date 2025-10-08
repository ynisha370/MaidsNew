import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  Clock,
  DollarSign,
  MapPin,
  Phone,
  User,
  Settings,
  LogOut,
  Bell,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Briefcase,
  Wallet,
  Star,
  Navigation,
  MessageSquare,
  Calendar as CalendarIcon,
  Timer,
  Car
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import JobsView from './JobsView';
import EarningsView from './EarningsView';
import DigitalWallet from './DigitalWallet';
import CleanerSettings from './CleanerSettings';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CleanerDashboard = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    todayJobs: [],
    upcomingJobs: [],
    earnings: {
      today: 0,
      thisWeek: 0,
      thisMonth: 0,
      total: 0
    },
    stats: {
      completedJobs: 0,
      totalEarnings: 0,
      rating: 0,
      onTimeRate: 0
    },
    notifications: []
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load dashboard overview data
      const [todayResponse, upcomingResponse, earningsResponse, statsResponse] = await Promise.all([
        axios.get(`${API}/cleaner/today-jobs`),
        axios.get(`${API}/cleaner/upcoming-jobs`),
        axios.get(`${API}/cleaner/earnings`),
        axios.get(`${API}/cleaner/stats`)
      ]);

      setDashboardData({
        todayJobs: todayResponse.data || [],
        upcomingJobs: upcomingResponse.data || [],
        earnings: earningsResponse.data || {},
        stats: statsResponse.data || {},
        notifications: [] // Can be loaded from separate endpoint
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    return timeString;
  };

  const handleClockIn = async (jobId) => {
    try {
      await axios.post(`${API}/cleaner/clock-in/${jobId}`);
      toast.success('Clocked in successfully!');
      loadDashboardData(); // Refresh data
    } catch (error) {
      toast.error('Failed to clock in');
    }
  };

  const handleClockOut = async (jobId) => {
    try {
      await axios.post(`${API}/cleaner/clock-out/${jobId}`);
      toast.success('Clocked out successfully!');
      loadDashboardData(); // Refresh data
    } catch (error) {
      toast.error('Failed to clock out');
    }
  };

  const handleUpdateETA = async (jobId, eta) => {
    try {
      await axios.post(`${API}/cleaner/update-eta/${jobId}`, { eta });
      toast.success('ETA updated successfully!');
    } catch (error) {
      toast.error('Failed to update ETA');
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Briefcase className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-semibold text-gray-900">Cleaner Dashboard</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4 mr-2" />
                Notifications
              </Button>
              <Button variant="outline" size="sm" onClick={() => navigate('/settings')}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900">
            {getGreeting()}, {user?.first_name}!
          </h2>
          <p className="text-gray-600 mt-1">
            Here's your schedule and earnings overview for today
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Today's Jobs</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.todayJobs.length}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DollarSign className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Today's Earnings</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    ${dashboardData.earnings.today?.toFixed(2) || '0.00'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Star className="h-8 w-8 text-yellow-500" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Rating</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.stats.rating?.toFixed(1) || '0.0'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TrendingUp className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">On-Time Rate</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {dashboardData.stats.onTimeRate || 0}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="jobs">My Jobs</TabsTrigger>
            <TabsTrigger value="earnings">Earnings</TabsTrigger>
            <TabsTrigger value="schedule">Schedule</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Today's Jobs */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CalendarIcon className="mr-2" size={20} />
                    Today's Jobs
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {dashboardData.todayJobs.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No jobs scheduled for today</p>
                  ) : (
                    <div className="space-y-4">
                      {dashboardData.todayJobs.map((job) => (
                        <div key={job.id} className="border rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h4 className="font-medium">{job.customer_name}</h4>
                              <p className="text-sm text-gray-500">{job.address}</p>
                            </div>
                            <Badge variant={job.status === 'confirmed' ? 'default' : 'secondary'}>
                              {job.status}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center text-sm text-gray-600">
                              <Clock className="mr-1" size={16} />
                              {formatTime(job.start_time)} - {formatTime(job.end_time)}
                            </div>
                            <div className="flex space-x-2">
                              {job.status === 'confirmed' && (
                                <>
                                  <Button size="sm" onClick={() => handleClockIn(job.id)}>
                                    Clock In
                                  </Button>
                                  <Button size="sm" variant="outline">
                                    <Navigation className="mr-1" size={16} />
                                    Directions
                                  </Button>
                                </>
                              )}
                              {job.status === 'in_progress' && (
                                <>
                                  <Button size="sm" onClick={() => handleClockOut(job.id)}>
                                    Clock Out
                                  </Button>
                                  <Button size="sm" variant="outline">
                                    <MessageSquare className="mr-1" size={16} />
                                    Contact
                                  </Button>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Earnings Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Wallet className="mr-2" size={20} />
                    Earnings Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Today</span>
                      <span className="font-medium">${dashboardData.earnings.today?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">This Week</span>
                      <span className="font-medium">${dashboardData.earnings.thisWeek?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">This Month</span>
                      <span className="font-medium">${dashboardData.earnings.thisMonth?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div className="flex justify-between items-center pt-2 border-t">
                      <span className="font-medium">Total Earnings</span>
                      <span className="font-bold text-lg">${dashboardData.earnings.total?.toFixed(2) || '0.00'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Jobs Tab */}
          <TabsContent value="jobs">
            <JobsView />
          </TabsContent>

          {/* Earnings Tab */}
          <TabsContent value="earnings">
            <EarningsView />
          </TabsContent>

          {/* Schedule Tab */}
          <TabsContent value="schedule">
            <DigitalWallet />
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings">
            <CleanerSettings />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CleanerDashboard;
