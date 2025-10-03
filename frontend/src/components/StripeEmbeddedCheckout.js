import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { loadStripe } from '@stripe/stripe-js';
import { AlertCircle, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Initialize Stripe with the provided key
const stripe = loadStripe("pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lR0w67");

const StripeEmbeddedCheckout = ({ bookingData, onPaymentSuccess, onPaymentError }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    initialize();
  }, []);

  // Create a Checkout Session
  async function initialize() {
    try {
      setLoading(true);
      setError(null);

      const fetchClientSecret = async () => {
        const response = await axios.post(`${API}/create-checkout-session`, {
          booking_id: bookingData.id,
          success_url: window.location.origin,
          cancel_url: window.location.origin
        });
        return response.data.clientSecret;
      };

      const checkout = await stripe.initEmbeddedCheckout({
        fetchClientSecret,
      });

      // Mount Checkout
      checkout.mount('#checkout');

      // Listen for checkout events
      checkout.on('complete', (event) => {
        if (event.session) {
          onPaymentSuccess(event.session);
          toast.success('Payment successful! Your booking is confirmed.');
        }
      });

      checkout.on('error', (event) => {
        const errorMessage = event.error?.message || 'Payment failed. Please try again.';
        onPaymentError(errorMessage);
        toast.error(errorMessage);
      });

      setLoading(false);
    } catch (err) {
      console.error('Failed to initialize checkout:', err);
      setError('Failed to load payment form. Please try again.');
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading secure payment form...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md mx-auto text-center">
          <AlertCircle className="h-16 w-16 mx-auto mb-4 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Payment Error</h2>
          <Alert className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <div className="space-x-4">
            <button 
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Try Again
            </button>
            <button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Return Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Secure Payment</h1>
          <p className="text-xl text-gray-600">Complete your booking with secure payment processing</p>
        </div>

        {/* Booking Summary */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Booking Summary</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Service:</span>
              <span className="font-medium">{bookingData.service_type || 'Standard Cleaning'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Date:</span>
              <span className="font-medium">{new Date(bookingData.booking_date).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Time:</span>
              <span className="font-medium">{bookingData.booking_time}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Customer:</span>
              <span className="font-medium">{bookingData.customer?.name || 'Guest'}</span>
            </div>
            <div className="flex justify-between text-lg font-bold border-t pt-2">
              <span>Total:</span>
              <span>${bookingData.total_amount?.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </div>

        {/* Stripe Embedded Checkout */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Payment Details</h2>
          <div id="checkout" className="min-h-[400px]">
            {/* Stripe checkout will be mounted here */}
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>🔒 Your payment information is secure and encrypted</p>
          <p>Powered by Stripe</p>
        </div>
      </div>
    </div>
  );
};

export default StripeEmbeddedCheckout;
