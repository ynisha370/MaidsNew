import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, CreditCard, Plus, Trash2, Star, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
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

// Debug: Log the key being used
console.log('Stripe Publishable Key:', STRIPE_PUBLISHABLE_KEY ? 'Loaded' : 'Missing');

const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY);

// Stripe Card Element Component
const StripeCardForm = ({ onSubmit, loading }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [cardholderName, setCardholderName] = useState('');
  const [isPrimary, setIsPrimary] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    const cardElement = elements.getElement(CardElement);

    const { error, paymentMethod } = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
      billing_details: {
        name: cardholderName,
      },
    });

    if (error) {
      toast.error(error.message);
    } else {
      onSubmit({
        stripe_payment_method_id: paymentMethod.id,
        cardholder_name: cardholderName,
        is_primary: isPrimary
      });
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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <Label htmlFor="cardholderName">Cardholder Name</Label>
        <Input
          id="cardholderName"
          placeholder="John Doe"
          value={cardholderName}
          onChange={(e) => setCardholderName(e.target.value)}
          required
        />
      </div>
      
      <div>
        <Label>Card Information</Label>
        <div className="mt-2 p-3 border border-gray-300 rounded-md">
          <CardElement options={cardElementOptions} />
        </div>
      </div>
      
      <div>
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={isPrimary}
            onChange={(e) => setIsPrimary(e.target.checked)}
          />
          <span className="text-sm text-gray-700">Set as primary payment method</span>
        </label>
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="submit"
          disabled={!stripe || loading}
          className="bg-primary hover:bg-primary-light"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Adding...
            </>
          ) : (
            'Add Payment Method'
          )}
        </Button>
      </div>
    </form>
  );
};

const StripePaymentInformation = () => {
  const navigate = useNavigate();
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    loadPaymentMethods();
  }, []);

  const loadPaymentMethods = async () => {
    try {
      const response = await axios.get(`${API}/payment-methods`);
      setPaymentMethods(response.data);
    } catch (error) {
      console.error('Failed to load payment methods:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = async (paymentData) => {
    setSubmitting(true);

    try {
      const response = await axios.post(`${API}/payment-methods`, paymentData);
      setPaymentMethods([...paymentMethods, response.data]);
      setShowAddForm(false);
      toast.success('Payment method added successfully');
    } catch (error) {
      toast.error('Failed to add payment method');
      console.error('Failed to add payment method:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSetPrimary = async (cardId) => {
    try {
      await axios.put(`${API}/payment-methods/${cardId}/set-primary`);
      loadPaymentMethods(); // Reload to get updated data
      toast.success('Primary payment method updated');
    } catch (error) {
      toast.error('Failed to update primary payment method');
      console.error('Failed to set primary:', error);
    }
  };

  const handleDeleteCard = async (cardId) => {
    if (paymentMethods.length <= 1) {
      toast.error('At least one active credit card must be on file to hold your appointments.');
      return;
    }

    setDeleting(cardId);
    try {
      await axios.delete(`${API}/payment-methods/${cardId}`);
      setPaymentMethods(paymentMethods.filter(card => card.id !== cardId));
      toast.success('Payment method removed');
    } catch (error) {
      toast.error('Failed to remove payment method');
      console.error('Failed to delete payment method:', error);
    } finally {
      setDeleting(null);
    }
  };

  const formatCardNumber = (lastFour) => {
    return `**** **** **** ${lastFour}`;
  };

  const getCardType = (brand) => {
    const brandMap = {
      'visa': 'Visa',
      'mastercard': 'Mastercard',
      'amex': 'American Express',
      'discover': 'Discover'
    };
    return brandMap[brand] || 'Credit Card';
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
        {/* Header */}
        <div className="mb-8">
          <Button
            onClick={() => navigate('/')}
            variant="outline"
            className="mb-4"
          >
            <ArrowLeft className="mr-2" size={16} />
            Back to Dashboard
          </Button>
          <h1 className="text-4xl font-bold text-gray-800">Payment Information</h1>
          <p className="text-xl text-gray-600 mt-2">Manage your saved payment methods securely with Stripe</p>
        </div>

        <div className="max-w-4xl mx-auto">
          {/* Saved Payment Methods */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="text-2xl flex items-center">
                <CreditCard className="mr-2" size={24} />
                Saved Payment Methods
              </CardTitle>
            </CardHeader>
            <CardContent>
              {paymentMethods.length === 0 ? (
                <div className="text-center py-8">
                  <CreditCard className="mx-auto mb-4 text-gray-400" size={48} />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No Payment Methods</h3>
                  <p className="text-gray-500 mb-4">Add a payment method to get started</p>
                  <Button
                    onClick={() => setShowAddForm(true)}
                    className="bg-primary hover:bg-primary-light"
                  >
                    <Plus className="mr-2" size={16} />
                    Add Payment Method
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {paymentMethods.map((card) => (
                    <div
                      key={card.id}
                      className={`flex items-center justify-between p-4 rounded-lg border ${
                        card.is_primary ? 'border-primary bg-primary/5' : 'border-gray-200'
                      }`}
                    >
                      <div className="flex items-center space-x-4">
                        <CreditCard className="text-gray-600" size={24} />
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold text-gray-800">
                              {formatCardNumber(card.last_four)}
                            </span>
                            {card.is_primary && (
                              <Badge variant="secondary" className="flex items-center">
                                <Star className="mr-1" size={12} />
                                Primary Card
                              </Badge>
                            )}
                          </div>
                          <div className="text-sm text-gray-600">
                            {getCardType(card.card_brand)} • Expires {card.expiry_month}/{card.expiry_year}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {!card.is_primary && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSetPrimary(card.id)}
                          >
                            Set Primary
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteCard(card.id)}
                          disabled={deleting === card.id || (paymentMethods.length === 1)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="mr-1" size={14} />
                          {deleting === card.id ? 'Removing...' : 'Remove'}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Add New Card Form */}
          {showAddForm && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="text-xl">Add New Payment Method</CardTitle>
              </CardHeader>
              <CardContent>
                <Elements stripe={stripePromise}>
                  <StripeCardForm onSubmit={handleAddCard} loading={submitting} />
                </Elements>
              </CardContent>
            </Card>
          )}

          {/* Add New Card Button */}
          {!showAddForm && (
            <div className="text-center">
              <Button
                onClick={() => setShowAddForm(true)}
                className="bg-primary hover:bg-primary-light"
              >
                <Plus className="mr-2" size={16} />
                Add New Card
              </Button>
            </div>
          )}

          {/* Security Notice */}
          <Alert className="mt-8">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Secure Payment Processing:</strong> Your payment information is securely processed by Stripe, 
              a PCI-compliant payment processor. We never store your full card details on our servers.
            </AlertDescription>
          </Alert>
        </div>
      </div>
    </div>
  );
};

export default StripePaymentInformation;
