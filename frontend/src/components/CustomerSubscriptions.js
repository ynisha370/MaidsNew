import React, { useState, useEffect } from 'react';
import { Calendar, Clock, DollarSign, Pause, Play, XCircle, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CustomerSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSubscriptions();
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
            onClick={loadSubscriptions}
            className="flex items-center mx-auto"
          >
            <RefreshCw className="mr-2" size={16} />
            Refresh Subscriptions
          </Button>
        </div>
      </div>
    </div>
  );
};

export default CustomerSubscriptions;
