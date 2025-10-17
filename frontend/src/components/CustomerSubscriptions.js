import React, { useState, useEffect } from 'react';
import { Calendar, Clock, DollarSign, Pause, Play, XCircle, RefreshCw, User, AlertCircle, Eye, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [jobAssignments, setJobAssignments] = useState([]);
  const [selectedSubscription, setSelectedSubscription] = useState(null);
  const [showJobDetails, setShowJobDetails] = useState(false);

  useEffect(() => {
    loadSubscriptions();
    loadJobAssignments();
  }, []);

  const loadSubscriptions = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/customer/subscriptions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setSubscriptions(response.data);
    } catch (error) {
      console.error('Failed to load subscriptions:', error);
      toast.error('Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const loadJobAssignments = async () => {
    try {
      const response = await axios.get(`${API}/customer/bookings`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setJobAssignments(response.data || []);
    } catch (error) {
      console.error('Failed to load job assignments:', error);
    }
  };

  const pauseSubscription = async (subscriptionId) => {
    try {
      await axios.post(`${API}/customer/subscriptions/${subscriptionId}/pause`, {}, {
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
      await axios.post(`${API}/customer/subscriptions/${subscriptionId}/resume`, {}, {
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
    if (window.confirm('Are you sure you want to cancel this subscription? This action cannot be undone.')) {
      try {
        await axios.post(`${API}/customer/subscriptions/${subscriptionId}/cancel`, {}, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        toast.success('Subscription cancelled successfully');
        loadSubscriptions();
      } catch (error) {
        console.error('Failed to cancel subscription:', error);
        toast.error('Failed to cancel subscription');
      }
    }
  };

  const getJobAssignmentsForSubscription = (subscriptionId) => {
    return jobAssignments.filter(job => job.subscription_id === subscriptionId);
  };

  const getBookingStatusBadge = (status) => {
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

  const getStatusBadge = (status) => {
    const statusColors = {
      active: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={`${statusColors[status] || 'bg-gray-100 text-gray-800'} border-0`}>
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </Badge>
    );
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">My Subscriptions</h1>
          <p className="text-xl text-gray-600">Manage your recurring cleaning services</p>
        </div>

        {subscriptions.length === 0 ? (
          <Card className="border-2 border-dashed border-gray-300">
            <CardContent className="p-12 text-center">
              <Calendar className="mx-auto mb-4 text-gray-400" size={48} />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No Active Subscriptions</h3>
              <p className="text-gray-500 mb-4">You don't have any recurring cleaning subscriptions.</p>
              <Button
                onClick={() => window.location.href = '/book'}
                className="bg-primary hover:bg-primary-light text-white"
              >
                <Calendar className="mr-2" size={16} />
                Create Your First Subscription
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {subscriptions.map((subscription) => (
              <Card key={subscription.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xl flex items-center">
                      <Calendar className="mr-2" size={20} />
                      Subscription #{subscription.id.slice(-8)}
                    </CardTitle>
                    {getStatusBadge(subscription.status)}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-700">Frequency</h4>
                      <Badge variant="outline" className="capitalize">
                        {subscription.frequency.replace('_', ' ')}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-700">Next Booking</h4>
                      <div className="flex items-center text-gray-600">
                        <Clock className="mr-2" size={16} />
                        <span>{formatDate(subscription.next_booking_date)}</span>
                      </div>
                      <p className="text-sm text-gray-500">{subscription.preferred_time_slot}</p>
                    </div>
                    
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-700">Amount</h4>
                      <div className="flex items-center text-2xl font-bold text-primary">
                        <DollarSign className="mr-1" size={20} />
                        {subscription.total_amount}
                      </div>
                      <p className="text-sm text-gray-500">per booking</p>
                    </div>
                  </div>

                  {subscription.address && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-semibold text-gray-700 mb-2">Service Address</h4>
                      <p className="text-gray-600">
                        {subscription.address.street}, {subscription.address.city}, 
                        {subscription.address.state} {subscription.address.zip_code}
                      </p>
                    </div>
                  )}

                  {subscription.special_instructions && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-semibold text-gray-700 mb-2">Special Instructions</h4>
                      <p className="text-gray-600">{subscription.special_instructions}</p>
                    </div>
                  )}

                  {/* Job Assignments Section */}
                  {subscription.status === 'active' && (
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-semibold text-gray-700 mb-3 flex items-center">
                        <User className="mr-2" size={16} />
                        Recent Job Assignments
                      </h4>
                      {(() => {
                        const jobs = getJobAssignmentsForSubscription(subscription.id);
                        if (jobs.length === 0) {
                          return (
                            <div className="text-center py-4 text-gray-500">
                              <AlertCircle className="mx-auto mb-2" size={24} />
                              <p className="text-sm">No job assignments yet</p>
                              <p className="text-xs">Jobs will appear here once assigned</p>
                            </div>
                          );
                        }
                        return (
                          <div className="space-y-2">
                            {jobs.slice(0, 3).map((job) => (
                              <div key={job.id} className="flex items-center justify-between p-2 bg-white rounded border">
                                <div className="flex items-center space-x-3">
                                  <div>
                                    <p className="text-sm font-medium">
                                      {formatDate(job.booking_date)} • {job.time_slot}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                      {job.cleaner_name ? `Assigned to ${job.cleaner_name}` : 'Pending assignment'}
                                    </p>
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {getBookingStatusBadge(job.status)}
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                      setSelectedSubscription(subscription);
                                      setShowJobDetails(true);
                                    }}
                                  >
                                    <Eye className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            ))}
                            {jobs.length > 3 && (
                              <p className="text-xs text-gray-500 text-center">
                                +{jobs.length - 3} more jobs
                              </p>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  <div className="mt-6 flex flex-wrap gap-3">
                    {subscription.status === 'active' ? (
                      <Button
                        variant="outline"
                        onClick={() => pauseSubscription(subscription.id)}
                        className="flex items-center"
                      >
                        <Pause className="mr-2" size={16} />
                        Pause Subscription
                      </Button>
                    ) : subscription.status === 'paused' ? (
                      <Button
                        variant="outline"
                        onClick={() => resumeSubscription(subscription.id)}
                        className="flex items-center"
                      >
                        <Play className="mr-2" size={16} />
                        Resume Subscription
                      </Button>
                    ) : null}
                    
                    <Button
                      variant="outline"
                      onClick={() => cancelSubscription(subscription.id)}
                      className="flex items-center text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <XCircle className="mr-2" size={16} />
                      Cancel Subscription
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-8 text-center">
          <Button
            variant="outline"
            onClick={() => {
              loadSubscriptions();
              loadJobAssignments();
            }}
            className="flex items-center mx-auto"
          >
            <RefreshCw className="mr-2" size={16} />
            Refresh Subscriptions
          </Button>
        </div>
      </div>

      {/* Job Details Modal */}
      <Dialog open={showJobDetails} onOpenChange={setShowJobDetails}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Job Assignment Details</DialogTitle>
          </DialogHeader>
          {selectedSubscription && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-gray-700">Subscription</h4>
                  <p className="text-sm text-gray-600">#{selectedSubscription.id.slice(-8)}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-700">Frequency</h4>
                  <p className="text-sm text-gray-600 capitalize">
                    {selectedSubscription.frequency.replace('_', ' ')}
                  </p>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-700 mb-3">Job Assignments</h4>
                {(() => {
                  const jobs = getJobAssignmentsForSubscription(selectedSubscription.id);
                  if (jobs.length === 0) {
                    return (
                      <div className="text-center py-8 text-gray-500">
                        <AlertCircle className="mx-auto mb-2" size={32} />
                        <p>No job assignments found</p>
                      </div>
                    );
                  }
                  return (
                    <div className="space-y-3">
                      {jobs.map((job) => (
                        <div key={job.id} className="p-4 border rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <div>
                              <h5 className="font-medium">#{job.id.slice(-8)}</h5>
                              <p className="text-sm text-gray-600">
                                {formatDate(job.booking_date)} • {job.time_slot}
                              </p>
                            </div>
                            {getBookingStatusBadge(job.status)}
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">Cleaner:</span>
                              <span className="ml-2 font-medium">
                                {job.cleaner_name || 'Not assigned'}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-500">Amount:</span>
                              <span className="ml-2 font-medium">${job.total_amount?.toFixed(2)}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">House Size:</span>
                              <span className="ml-2 font-medium">{job.house_size}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">Assignment:</span>
                              <span className="ml-2 font-medium">
                                {job.assignment_type === 'auto' ? 'Automatic' : 'Manual'}
                              </span>
                            </div>
                          </div>
                          
                          {job.cleaner_notes && (
                            <div className="mt-3 p-2 bg-gray-50 rounded text-sm">
                              <span className="text-gray-500">Cleaner Notes:</span>
                              <p className="mt-1">{job.cleaner_notes}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  );
                })()}
              </div>
              
              <div className="flex justify-end pt-4">
                <Button variant="outline" onClick={() => setShowJobDetails(false)}>
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default CustomerSubscriptions;
