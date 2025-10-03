import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import axios from 'axios';
import StripeEmbeddedCheckout from './StripeEmbeddedCheckout';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PaymentPage = () => {
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [bookingData, setBookingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paymentStatus, setPaymentStatus] = useState('pending');

  useEffect(() => {
    loadBookingData();
  }, [bookingId]);

  const loadBookingData = async () => {
    try {
      const response = await axios.get(`${API}/bookings/${bookingId}`);
      setBookingData(response.data);
    } catch (error) {
      console.error('Failed to load booking:', error);
      toast.error('Failed to load booking details');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSuccess = (paymentResult) => {
    setPaymentStatus('success');
    toast.success('Payment successful! Your booking is confirmed.');
    
    // Redirect to confirmation page after a short delay
    setTimeout(() => {
      navigate(`/confirmation/${bookingId}`);
    }, 2000);
  };

  const handlePaymentError = (errorMessage) => {
    setPaymentStatus('error');
    toast.error(errorMessage);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading booking details...</p>
        </div>
      </div>
    );
  }

  if (!bookingData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-500" />
          <p>Booking not found</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            Return Home
          </Button>
        </div>
      </div>
    );
  }

  if (paymentStatus === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md mx-auto text-center">
          <CardContent className="p-8">
            <CheckCircle className="h-16 w-16 mx-auto mb-4 text-green-500" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Successful!</h2>
            <p className="text-gray-600 mb-4">
              Your booking has been confirmed and payment processed successfully.
            </p>
            <div className="space-y-2 text-sm text-gray-500">
              <p>Booking ID: #{bookingData.id.slice(-8)}</p>
              <p>Date: {new Date(bookingData.booking_date).toLocaleDateString()}</p>
              <p>Time: {bookingData.time_slot}</p>
            </div>
            <Button 
              onClick={() => navigate(`/confirmation/${bookingId}`)}
              className="mt-6 w-full"
            >
              View Booking Details
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (paymentStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md mx-auto text-center">
          <CardContent className="p-8">
            <AlertCircle className="h-16 w-16 mx-auto mb-4 text-red-500" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Failed</h2>
            <p className="text-gray-600 mb-4">
              There was an issue processing your payment. Please try again.
            </p>
            <div className="space-x-4">
              <Button 
                onClick={() => setPaymentStatus('pending')}
                variant="outline"
              >
                Try Again
              </Button>
              <Button 
                onClick={() => navigate('/')}
              >
                Return Home
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <StripeEmbeddedCheckout
      bookingData={bookingData}
      onPaymentSuccess={handlePaymentSuccess}
      onPaymentError={handlePaymentError}
    />
  );
};

export default PaymentPage;
