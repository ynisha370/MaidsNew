import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CreditCard, Lock, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { toast } from 'sonner';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Initialize Stripe
const STRIPE_PUBLISHABLE_KEY = process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || 'pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67';
const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);

// Stripe Payment Form Component
const StripePaymentForm = ({ bookingData, onPaymentSuccess, onPaymentError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [savedPaymentMethods, setSavedPaymentMethods] = useState([]);
  const [useSavedMethod, setUseSavedMethod] = useState(false);
  const [cardholderName, setCardholderName] = useState('');

  useEffect(() => {
    loadSavedPaymentMethods();
  }, []);

  const loadSavedPaymentMethods = async () => {
    try {
      const response = await axios.get(`${API}/payment-methods`);
      setSavedPaymentMethods(response.data);
      if (response.data.length > 0) {
        setUseSavedMethod(true);
        setPaymentMethod(response.data.find(pm => pm.is_primary) || response.data[0]);
      }
    } catch (error) {
      console.error('Failed to load payment methods:', error);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setProcessing(true);

    try {
      let paymentMethodId = null;

      if (useSavedMethod && paymentMethod) {
        // Use saved payment method
        paymentMethodId = paymentMethod.stripe_payment_method_id;
      } else {
        // Create new payment method
        const cardElement = elements.getElement(CardElement);
        const { error, paymentMethod: newPaymentMethod } = await stripe.createPaymentMethod({
          type: 'card',
          card: cardElement,
          billing_details: {
            name: cardholderName,
          },
        });

        if (error) {
          throw new Error(error.message);
        }

        paymentMethodId = newPaymentMethod.id;
      }

      // Create payment intent
      const paymentIntentResponse = await axios.post(`${API}/payment-intents`, {
        booking_id: bookingData.id,
        amount: Math.round(bookingData.total_amount * 100), // Convert to cents
        payment_method_id: paymentMethodId
      });

      const paymentIntent = paymentIntentResponse.data;

      // Confirm payment
      const confirmResponse = await axios.post(
        `${API}/payment-intents/${paymentIntent.id}/confirm`
      );

      if (confirmResponse.data.status === 'succeeded') {
        onPaymentSuccess(confirmResponse.data);
      } else {
        throw new Error('Payment was not successful');
      }

    } catch (error) {
      console.error('Payment error:', error);
      onPaymentError(error.message || 'Payment failed. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: '16px',
        color: '#424770',
        '::placeholder': {
          color: '#aab7c4',
        },
      },
      invalid: {
        color: '#9e2146',
      },
    },
  };

  return (
    <div className="space-y-6">
      {/* Payment Method Selection */}
      {savedPaymentMethods.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Choose Payment Method</h3>
          
          <div className="space-y-3">
            <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="paymentMethod"
                checked={useSavedMethod}
                onChange={() => setUseSavedMethod(true)}
              />
              <div className="flex-1">
                <div className="font-medium">Use Saved Payment Method</div>
                <div className="text-sm text-gray-600">
                  {paymentMethod ? `**** **** **** ${paymentMethod.last_four}` : 'Select a saved method'}
                </div>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
              <input
                type="radio"
                name="paymentMethod"
                checked={!useSavedMethod}
                onChange={() => setUseSavedMethod(false)}
              />
              <div className="flex-1">
                <div className="font-medium">Use New Payment Method</div>
                <div className="text-sm text-gray-600">Enter new card details</div>
              </div>
            </label>
          </div>

          {useSavedMethod && (
            <div className="ml-6">
              <select
                value={paymentMethod?.id || ''}
                onChange={(e) => {
                  const selected = savedPaymentMethods.find(pm => pm.id === e.target.value);
                  setPaymentMethod(selected);
                }}
                className="w-full p-2 border border-gray-300 rounded-md"
              >
                {savedPaymentMethods.map((method) => (
                  <option key={method.id} value={method.id}>
                    {method.card_brand.toUpperCase()} **** {method.last_four} 
                    {method.is_primary ? ' (Primary)' : ''}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      )}

      {/* New Card Form */}
      {!useSavedMethod && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Card Information</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cardholder Name
            </label>
            <input
              type="text"
              placeholder="John Doe"
              value={cardholderName}
              onChange={(e) => setCardholderName(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-md"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Card Details
            </label>
            <div className="p-3 border border-gray-300 rounded-md">
              <CardElement options={cardElementOptions} />
            </div>
          </div>
        </div>
      )}

      {/* Payment Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Payment Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Service Total:</span>
              <span>${bookingData.total_amount?.toFixed(2) || '0.00'}</span>
            </div>
            <div className="flex justify-between font-semibold text-lg border-t pt-2">
              <span>Total:</span>
              <span>${bookingData.total_amount?.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <Button
        onClick={handleSubmit}
        disabled={!stripe || processing}
        className="w-full bg-primary hover:bg-primary-light text-white py-3 text-lg"
      >
        {processing ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Processing Payment...
          </>
        ) : (
          <>
            <Lock className="mr-2 h-5 w-5" />
            Pay ${bookingData.total_amount?.toFixed(2) || '0.00'}
          </>
        )}
      </Button>

      {/* Security Notice */}
      <Alert>
        <Lock className="h-4 w-4" />
        <AlertDescription>
          Your payment information is securely processed by Stripe. We never store your card details.
        </AlertDescription>
      </Alert>
    </div>
  );
};

const StripeCheckout = ({ bookingData, onPaymentSuccess, onPaymentError }) => {
  const navigate = useNavigate();
  const [stripeLoaded, setStripeLoaded] = useState(false);

  useEffect(() => {
    // Check if Stripe is loaded
    stripePromise.then(() => setStripeLoaded(true));
  }, []);

  if (!stripeLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading secure payment form...</p>
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
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <CreditCard className="mr-2" size={20} />
              Booking Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Date:</span>
                <span>{new Date(bookingData.booking_date).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Time:</span>
                <span>{bookingData.time_slot}</span>
              </div>
              <div className="flex justify-between">
                <span>Service:</span>
                <span>{bookingData.house_size} sq ft • {bookingData.frequency}</span>
              </div>
              <div className="flex justify-between font-semibold text-lg border-t pt-2">
                <span>Total:</span>
                <span>${bookingData.total_amount?.toFixed(2) || '0.00'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Payment Form */}
        <Elements stripe={stripePromise}>
          <StripePaymentForm
            bookingData={bookingData}
            onPaymentSuccess={onPaymentSuccess}
            onPaymentError={onPaymentError}
          />
        </Elements>
      </div>
    </div>
  );
};

export default StripeCheckout;
