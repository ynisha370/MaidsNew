import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  MapPin,
  Phone,
  User,
  CheckCircle,
  AlertCircle,
  Play,
  Pause,
  Navigation,
  MessageSquare,
  Filter,
  Search,
  MoreVertical,
  Eye,
  Edit,
  Trash2,
  Star,
  DollarSign,
  Timer,
  Car
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const JobsView = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDate, setFilterDate] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const [showJobDetails, setShowJobDetails] = useState(false);

  useEffect(() => {
    loadJobs();
  }, [filterStatus, filterDate]);

  const loadJobs = async () => {
    try {
      setLoading(true);

      // Build query parameters
      const params = new URLSearchParams();
      if (filterStatus !== 'all') params.append('status', filterStatus);
      if (filterDate !== 'all') params.append('date_range', filterDate);

      const response = await axios.get(`${API}/cleaner/jobs?${params}`);
      // Support both {jobs: []} and [] response shapes
      const data = response.data;
      setJobs(Array.isArray(data) ? data : (data?.jobs || []));
    } catch (error) {
      console.error('Failed to load jobs:', error);
      toast.error('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleClockIn = async (jobId) => {
    try {
      await axios.post(`${API}/cleaner/clock-in/${jobId}`);
      toast.success('Clocked in successfully!');
      loadJobs(); // Refresh data
    } catch (error) {
      toast.error('Failed to clock in');
    }
  };

  const handleClockOut = async (jobId) => {
    try {
      await axios.post(`${API}/cleaner/clock-out/${jobId}`);
      toast.success('Clocked out successfully!');
      loadJobs(); // Refresh data
    } catch (error) {
      toast.error('Failed to clock out');
    }
  };

  const handleUpdateETA = async (jobId, eta) => {
    try {
      await axios.post(`${API}/cleaner/update-eta/${jobId}`, { eta });
      toast.success('ETA updated successfully!');
      setSelectedJob(null);
    } catch (error) {
      toast.error('Failed to update ETA');
    }
  };

  const handleJobAction = async (jobId, action) => {
    try {
      await axios.post(`${API}/cleaner/job-action/${jobId}`, { action });
      toast.success(`Job ${action} successfully!`);
      loadJobs(); // Refresh data
    } catch (error) {
      toast.error(`Failed to ${action} job`);
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-green-100 text-green-800';
      case 'completed': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredJobs = jobs.filter(job => {
    if (searchTerm && !job.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !job.address.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <Input
                  placeholder="Search by customer name or address..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterDate} onValueChange={setFilterDate}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Filter by date" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Dates</SelectItem>
                  <SelectItem value="today">Today</SelectItem>
                  <SelectItem value="tomorrow">Tomorrow</SelectItem>
                  <SelectItem value="week">This Week</SelectItem>
                  <SelectItem value="month">This Month</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Jobs List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-lg">{job.customer_name}</h3>
                    <Badge className={getStatusColor(job.status)}>
                      {job.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex items-center text-gray-600 mb-2">
                    <MapPin className="mr-2" size={16} />
                    <span className="text-sm">{job.address}</span>
                  </div>
                  <div className="flex items-center text-gray-600 mb-2">
                    <Phone className="mr-2" size={16} />
                    <span className="text-sm">{job.customer_phone}</span>
                  </div>
                  <div className="flex items-center text-gray-600 mb-3">
                    <Calendar className="mr-2" size={16} />
                    <span className="text-sm">{formatDate(job.date)}</span>
                  </div>
                  <div className="flex items-center text-gray-600 mb-3">
                    <Clock className="mr-2" size={16} />
                    <span className="text-sm">{formatTime(job.start_time)} - {formatTime(job.end_time)}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600 mb-1">
                    ${job.total_amount}
                  </div>
                  <div className="text-sm text-gray-500">
                    {job.duration_hours}h
                  </div>
                </div>
              </div>

              {/* Job Actions */}
              <div className="flex flex-wrap gap-2">
                {job.status === 'confirmed' && (
                  <>
                    <Button size="sm" onClick={() => handleClockIn(job.id)}>
                      <Play className="mr-1" size={16} />
                      Clock In
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setSelectedJob(job)}>
                      <Timer className="mr-1" size={16} />
                      Update ETA
                    </Button>
                  </>
                )}
                {job.status === 'in_progress' && (
                  <>
                    <Button size="sm" onClick={() => handleClockOut(job.id)}>
                      <Pause className="mr-1" size={16} />
                      Clock Out
                    </Button>
                    <Button size="sm" variant="outline">
                      <MessageSquare className="mr-1" size={16} />
                      Contact
                    </Button>
                  </>
                )}
                {job.status === 'completed' && (
                  <Badge className="bg-green-100 text-green-800">
                    <CheckCircle className="mr-1" size={16} />
                    Completed
                  </Badge>
                )}
                <Button size="sm" variant="outline" onClick={() => {
                  setSelectedJob(job);
                  setShowJobDetails(true);
                }}>
                  <Eye className="mr-1" size={16} />
                  Details
                </Button>
              </div>

              {/* Special Instructions */}
              {job.special_instructions && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm font-medium text-blue-900 mb-1">Special Instructions:</p>
                  <p className="text-sm text-blue-800">{job.special_instructions}</p>
                </div>
              )}

              {/* Job Progress Indicator */}
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                  <span>Progress</span>
                  <span>
                    {job.status === 'confirmed' && 'Ready to start'}
                    {job.status === 'in_progress' && 'In progress'}
                    {job.status === 'completed' && 'Completed'}
                    {job.status === 'cancelled' && 'Cancelled'}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${
                      job.status === 'confirmed' ? 'bg-blue-500 w-1/3' :
                      job.status === 'in_progress' ? 'bg-green-500 w-2/3' :
                      job.status === 'completed' ? 'bg-green-600 w-full' :
                      'bg-red-500 w-full'
                    }`}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredJobs.length === 0 && (
        <div className="text-center py-12">
          <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-500">
            {searchTerm || filterStatus !== 'all' || filterDate !== 'all'
              ? 'Try adjusting your filters or search terms'
              : 'You have no jobs scheduled'}
          </p>
        </div>
      )}

      {/* Job Details Modal */}
      <Dialog open={showJobDetails} onOpenChange={setShowJobDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Job Details</DialogTitle>
          </DialogHeader>
          {selectedJob && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Customer Information</h4>
                  <p className="text-sm text-gray-600">{selectedJob.customer_name}</p>
                  <p className="text-sm text-gray-600">{selectedJob.customer_email}</p>
                  <p className="text-sm text-gray-600">{selectedJob.customer_phone}</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Job Information</h4>
                  <p className="text-sm text-gray-600">{formatDate(selectedJob.date)}</p>
                  <p className="text-sm text-gray-600">{formatTime(selectedJob.start_time)} - {formatTime(selectedJob.end_time)}</p>
                  <p className="text-sm text-gray-600">${selectedJob.total_amount}</p>
                </div>
              </div>

              <div>
                <h4 className="font-medium text-gray-900 mb-2">Address</h4>
                <p className="text-sm text-gray-600">{selectedJob.address}</p>
              </div>

              {selectedJob.services && selectedJob.services.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Services</h4>
                  <div className="space-y-2">
                    {selectedJob.services.map((service, index) => (
                      <div key={index} className="flex justify-between items-center text-sm">
                        <span>{service.name}</span>
                        <span>${service.price}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedJob.special_instructions && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Special Instructions</h4>
                  <p className="text-sm text-gray-600">{selectedJob.special_instructions}</p>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setShowJobDetails(false)}>
                  Close
                </Button>
                {selectedJob.status === 'confirmed' && (
                  <Button onClick={() => handleClockIn(selectedJob.id)}>
                    Start Job
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* ETA Update Modal */}
      <Dialog open={!!selectedJob && !showJobDetails} onOpenChange={() => setSelectedJob(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update ETA</DialogTitle>
          </DialogHeader>
          {selectedJob && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estimated Arrival Time
                </label>
                <Input
                  type="time"
                  defaultValue={selectedJob.eta || ''}
                  onChange={(e) => {
                    if (selectedJob) {
                      setSelectedJob({...selectedJob, eta: e.target.value});
                    }
                  }}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button variant="outline" onClick={() => setSelectedJob(null)}>
                  Cancel
                </Button>
                <Button onClick={() => handleUpdateETA(selectedJob.id, selectedJob.eta)}>
                  Update ETA
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default JobsView;
