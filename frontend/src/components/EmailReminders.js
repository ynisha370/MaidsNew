import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import axios from 'axios';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const EmailReminders = () => {
  const [upcomingBookings, setUpcomingBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedBookings, setSelectedBookings] = useState([]);
  const [reminderType, setReminderType] = useState('upcoming');
  const [daysAhead, setDaysAhead] = useState(7);
  const [sendingEmails, setSendingEmails] = useState(false);
  const [emailStats, setEmailStats] = useState(null);

  useEffect(() => {
    loadUpcomingBookings();
  }, [daysAhead]);

  const loadUpcomingBookings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/admin/email-reminders/upcoming?days_ahead=${daysAhead}`);
      setUpcomingBookings(response.data.bookings);
    } catch (error) {
      toast.error('Failed to load upcoming bookings');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleBookingSelect = (bookingId) => {
    setSelectedBookings(prev => 
      prev.includes(bookingId) 
        ? prev.filter(id => id !== bookingId)
        : [...prev, bookingId]
    );
  };

  const handleSelectAll = () => {
    const bookingsWithEmail = upcomingBookings.filter(booking => booking.has_email);
    if (selectedBookings.length === bookingsWithEmail.length) {
      setSelectedBookings([]);
    } else {
      setSelectedBookings(bookingsWithEmail.map(booking => booking.id));
    }
  };

  const sendSingleReminder = async (bookingId) => {
    try {
      setSendingEmails(true);
      await axios.post(`${API}/admin/email-reminders/send-single`, {
        booking_id: bookingId,
        reminder_type: reminderType
      });
      toast.success('Email reminder sent successfully');
    } catch (error) {
      toast.error('Failed to send email reminder');
      console.error(error);
    } finally {
      setSendingEmails(false);
    }
  };

  const sendBatchReminders = async () => {
    if (selectedBookings.length === 0) {
      toast.warning('Please select at least one booking');
      return;
    }

    try {
      setSendingEmails(true);
      const response = await axios.post(`${API}/admin/email-reminders/send-batch`, {
        booking_ids: selectedBookings,
        reminder_type: reminderType
      });
      
      setEmailStats(response.data);
      toast.success(`Batch emails sent: ${response.data.emails_sent} successful, ${response.data.emails_failed} failed`);
      setSelectedBookings([]);
    } catch (error) {
      toast.error('Failed to send batch email reminders');
      console.error(error);
    } finally {
      setSendingEmails(false);
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

  const getReminderTypeLabel = (type) => {
    const labels = {
      'upcoming': 'General Reminder',
      'day_before': 'Day Before',
      'week_before': 'Week Before',
      'confirmation': 'Confirmation',
      'cancelled': 'Cancellation'
    };
    return labels[type] || type;
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Email Reminders</h2>
        <p className="text-gray-600">Send personalized email reminders to your customers about their upcoming cleaning appointments.</p>
      </div>

      {/* Controls */}
      <div className="mb-6 bg-gray-50 p-4 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Days Ahead
            </label>
            <select
              value={daysAhead}
              onChange={(e) => setDaysAhead(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 Day</option>
              <option value={3}>3 Days</option>
              <option value={7}>7 Days</option>
              <option value={14}>14 Days</option>
              <option value={30}>30 Days</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reminder Type
            </label>
            <select
              value={reminderType}
              onChange={(e) => setReminderType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="upcoming">General Reminder</option>
              <option value="day_before">Day Before</option>
              <option value="week_before">Week Before</option>
              <option value="confirmation">Confirmation</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadUpcomingBookings}
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Batch Actions */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={handleSelectAll}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            {selectedBookings.length === upcomingBookings.filter(b => b.has_email).length ? 'Deselect All' : 'Select All'}
          </button>
          
          <button
            onClick={sendBatchReminders}
            disabled={selectedBookings.length === 0 || sendingEmails}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {sendingEmails ? 'Sending...' : `Send to ${selectedBookings.length} Selected`}
          </button>
        </div>
      </div>

      {/* Email Stats */}
      {emailStats && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-800 mb-2">Email Send Results</h3>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="font-medium">Total:</span> {emailStats.total_bookings}
            </div>
            <div>
              <span className="font-medium text-green-600">Sent:</span> {emailStats.emails_sent}
            </div>
            <div>
              <span className="font-medium text-red-600">Failed:</span> {emailStats.emails_failed}
            </div>
          </div>
        </div>
      )}

      {/* Bookings List */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-800">
            Upcoming Bookings ({upcomingBookings.length})
          </h3>
        </div>

        {loading ? (
          <div className="p-8 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading bookings...</p>
          </div>
        ) : upcomingBookings.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <p>No upcoming bookings found for the selected time period.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <input
                      type="checkbox"
                      checked={selectedBookings.length === upcomingBookings.filter(b => b.has_email).length && upcomingBookings.filter(b => b.has_email).length > 0}
                      onChange={handleSelectAll}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date & Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {upcomingBookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        checked={selectedBookings.includes(booking.id)}
                        onChange={() => handleBookingSelect(booking.id)}
                        disabled={!booking.has_email}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {booking.customer_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {booking.customer_email || 'No email available'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatDate(booking.booking_date)}
                      </div>
                      <div className="text-sm text-gray-500">
                        {booking.time_slot}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${booking.total_amount.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        booking.status === 'confirmed' 
                          ? 'bg-green-100 text-green-800'
                          : booking.status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {booking.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {booking.has_email ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          ✓ Available
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                          ✗ No Email
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => sendSingleReminder(booking.id)}
                        disabled={!booking.has_email || sendingEmails}
                        className="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {sendingEmails ? 'Sending...' : 'Send Reminder'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="font-semibold text-yellow-800 mb-2">💡 Tips for Email Reminders</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Select multiple bookings to send batch reminders</li>
          <li>• Use "Day Before" reminders for confirmed appointments</li>
          <li>• "Week Before" reminders work well for recurring customers</li>
          <li>• Only bookings with valid email addresses can receive reminders</li>
          <li>• Check your AWS SES configuration for email delivery</li>
        </ul>
      </div>
    </div>
  );
};

export default EmailReminders;
