import React, { useState } from 'react';
import { X, AlertTriangle, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CancellationRequestModal = ({ isOpen, onClose, booking }) => {
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) {
      toast.error('Please provide a reason for cancellation');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/cancellation-requests`, 
        {
          booking_id: booking.id,
          reason: reason.trim()
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setSubmitted(true);
      toast.success('Cancellation request submitted successfully!');
    } catch (error) {
      console.error('Cancellation request error:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit cancellation request');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setReason('');
    setSubmitted(false);
    onClose();
  };

  if (!isOpen) return null;

  if (submitted) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="p-6 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Request Submitted</h3>
            <p className="text-gray-600 mb-4">
              Your cancellation request has been submitted and is under review. 
              You will be notified once it's processed.
            </p>
            <Button onClick={handleClose} className="w-full">
              Close
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-lg mx-4">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-xl">Request Cancellation</CardTitle>
          <Button variant="ghost" size="sm" onClick={handleClose}>
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Warning Alert */}
            <Alert className="border-orange-200 bg-orange-50">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-orange-800">
                <strong>Cancellation Policy:</strong> Cancellation requests require admin approval. 
                If this is a recurring service cancelled before the third cleaning, a $200 early 
                cancellation fee may apply.
              </AlertDescription>
            </Alert>

            {/* Booking Details */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Booking Details:</h4>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                <div>
                  <span className="font-medium">Date:</span> {new Date(booking.booking_date).toLocaleDateString()}
                </div>
                <div>
                  <span className="font-medium">Time:</span> {booking.time_slot}
                </div>
                <div>
                  <span className="font-medium">Frequency:</span> {booking.frequency}
                </div>
                <div>
                  <span className="font-medium">Total:</span> ${booking.total_amount?.toFixed(2) || '0.00'}
                </div>
              </div>
            </div>

            {/* Cancellation Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Reason for Cancellation *
                </label>
                <Textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  placeholder="Please provide a detailed reason for cancelling this booking..."
                  rows={4}
                  required
                />
              </div>

              <div className="flex space-x-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={loading || !reason.trim()}
                  className="flex-1 bg-red-600 hover:bg-red-700"
                >
                  {loading ? (
                    <>
                      <Clock className="mr-2 h-4 w-4 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <XCircle className="mr-2 h-4 w-4" />
                      Submit Request
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CancellationRequestModal;
