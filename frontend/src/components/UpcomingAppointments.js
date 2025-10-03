import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Calendar, Clock, ArrowLeft, DollarSign } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const UpcomingAppointments = () => {
  const navigate = useNavigate();
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUpcomingAppointments();
  }, []);

  const loadUpcomingAppointments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/customer/upcoming-appointments`);
      if (Array.isArray(response.data)) {
        setUpcomingAppointments(response.data);
      }
    } catch (error) {
      console.error('Failed to load upcoming appointments:', error);
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

  const formatTime = (timeSlot) => {
    if (!timeSlot) return 'Time TBD';
    return timeSlot;
  };

  const handleBackToDashboard = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Loading upcoming appointments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header with Back Button */}
        <div className="mb-8">
          <Button
            variant="outline"
            onClick={handleBackToDashboard}
            className="mb-4"
          >
            <ArrowLeft className="mr-2" size={16} />
            Back to Dashboard
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Calendar className="mr-3" size={32} />
            Upcoming Appointments
          </h1>
          <p className="text-gray-600 mt-2">
            View and manage your upcoming cleaning appointments
          </p>
        </div>

        {/* Appointments List */}
        {upcomingAppointments.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Calendar className="mx-auto mb-4 text-gray-400" size={48} />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Upcoming Appointments
              </h3>
              <p className="text-gray-600 mb-4">
                You don't have any upcoming appointments scheduled.
              </p>
              <Button onClick={() => navigate('/book')}>
                Book New Appointment
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {upcomingAppointments.map((appointment, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-3">
                        <Calendar className="mr-2 text-blue-600" size={20} />
                        <h3 className="text-lg font-semibold text-gray-900">
                          {formatDate(appointment.booking_date)}
                        </h3>
                      </div>
                      
                      <div className="flex items-center mb-2">
                        <Clock className="mr-2 text-gray-500" size={16} />
                        <span className="text-gray-700">
                          {formatTime(appointment.time_slot)}
                        </span>
                      </div>

                      {appointment.frequency && (
                        <div className="mb-2">
                          <Badge variant="outline" className="text-xs">
                            {appointment.frequency.replace('_', ' ').toUpperCase()}
                          </Badge>
                        </div>
                      )}

                      {appointment.total_amount && (
                        <div className="flex items-center">
                          <DollarSign className="mr-1 text-green-600" size={16} />
                          <span className="text-lg font-semibold text-green-600">
                            ${appointment.total_amount.toFixed(2)}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex flex-col space-y-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate('/reschedule')}
                      >
                        Reschedule
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate('/edit-cleaning')}
                      >
                        Edit Details
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => navigate('/book')}
              >
                <Calendar className="mr-2" size={16} />
                Book New Appointment
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => navigate('/payment-history')}
              >
                <DollarSign className="mr-2" size={16} />
                View Payment History
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UpcomingAppointments;
