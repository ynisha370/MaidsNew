import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { MessageSquare, Phone, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const ReminderStatus = ({ bookingId }) => {
  const [reminderLogs, setReminderLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (bookingId) {
      loadReminderLogs();
    }
  }, [bookingId]);

  const loadReminderLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/reminders/logs?booking_id=${bookingId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setReminderLogs(data.logs);
      }
    } catch (error) {
      console.error('Error loading reminder logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sent':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />;
      default:
        return <MessageSquare className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'sent': { variant: 'default', color: 'bg-green-100 text-green-800' },
      'failed': { variant: 'destructive', color: 'bg-red-100 text-red-800' },
      'pending': { variant: 'secondary', color: 'bg-yellow-100 text-yellow-800' }
    };
    const config = variants[status] || variants['pending'];
    
    return (
      <Badge variant={config.variant} className={config.color}>
        {status}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (!bookingId) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Phone className="w-5 h-5" />
          Text Message Reminders
        </CardTitle>
        <CardDescription>
          View the status of text message reminders sent for this booking
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-600 mt-2">Loading reminder status...</p>
          </div>
        ) : reminderLogs.length === 0 ? (
          <div className="text-center py-4">
            <MessageSquare className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">No reminders sent yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reminderLogs.map((log) => (
              <div key={log.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  {getStatusIcon(log.status)}
                  <div>
                    <p className="text-sm font-medium">Reminder Sent</p>
                    <p className="text-xs text-gray-600">
                      {formatDate(log.sent_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {getStatusBadge(log.status)}
                </div>
              </div>
            ))}
          </div>
        )}
        
        <div className="mt-4 pt-4 border-t">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={loadReminderLogs}
            disabled={loading}
            className="w-full"
          >
            Refresh Status
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReminderStatus;
