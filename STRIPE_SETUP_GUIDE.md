# Stripe Payment Integration Setup Guide

## Overview
This guide will help you set up the complete Stripe payment integration for the Maids of Cyfair booking system with robust security measures.

## Prerequisites
- Node.js and npm installed
- Python 3.8+ installed
- MongoDB running locally
- Stripe account with test keys

## Your Stripe Keys
Based on your Stripe dashboard, here are your test keys:

**Publishable Key (Frontend):**
```
pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67
```

**Secret Key (Backend):**
```
sk_test_51RzKQdRps3Ulo01CBYdM3Yeq7KsXP3remjM3drLFEamLjXPd2troAmutNVBrJ3Y5fVCSaMxGwOaCWgPwHvYqKx8o00KoqztCIz
```

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the backend directory:

```bash
# Database Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=maidsofcyfair

# JWT Configuration
JWT_SECRET=maids_secret_key_2024
JWT_ALGORITHM=HS256

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_51RzKQdRps3Ulo01CBYdM3Yeq7KsXP3remjM3drLFEamLjXPd2troAmutNVBrJ3Y5fVCSaMxGwOaCWgPwHvYqKx8o00KoqztCIz
STRIPE_PUBLISHABLE_KEY=pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Google Calendar API (Optional)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/calendar/callback
```

### 3. Start Backend Server
```bash
python server.py
```

The server will start on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Configuration
Create a `.env` file in the frontend directory:

```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8000

# Stripe Configuration
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67
```

### 3. Start Frontend Server
```bash
npm start
```

The frontend will start on `http://localhost:3000`

## Stripe Webhook Setup

### 1. Install Stripe CLI
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Windows
# Download from https://github.com/stripe/stripe-cli/releases
```

### 2. Login to Stripe
```bash
stripe login
```

### 3. Forward Webhooks to Local Server
```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Copy the webhook signing secret and update your `.env` file:
```
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_from_cli
```

## Testing the Integration

### 1. Test Cards
Use these Stripe test cards for testing:

**Successful Payment:**
- Card: `4242 4242 4242 4242`
- CVC: Any 3 digits
- Expiry: Any future date

**Declined Payment:**
- Card: `4000 0000 0000 0002`
- CVC: Any 3 digits
- Expiry: Any future date

**3D Secure Authentication:**
- Card: `4000 0025 0000 3155`
- CVC: Any 3 digits
- Expiry: Any future date

### 2. Test Flow
1. Register a new user account
2. Navigate to `/payment` to add a payment method
3. Create a booking at `/book`
4. Complete payment during booking flow
5. Verify payment in Stripe dashboard

## Security Features Implemented

### Backend Security
- ✅ Input validation (Luhn algorithm for card numbers)
- ✅ JWT authentication for all payment endpoints
- ✅ User authorization (users can only access their own data)
- ✅ Stripe webhook signature verification
- ✅ No sensitive data storage (only Stripe references)
- ✅ Comprehensive error handling

### Frontend Security
- ✅ Stripe Elements for PCI-compliant card handling
- ✅ No card data touches our servers
- ✅ Secure tokenization through Stripe
- ✅ Real-time validation
- ✅ HTTPS enforcement (in production)

### Payment Flow Security
- ✅ Server-side payment intent creation
- ✅ Amount validation on backend
- ✅ Idempotency keys for duplicate prevention
- ✅ Webhook verification for payment confirmations
- ✅ 3D Secure authentication support

## API Endpoints

### Payment Methods
- `GET /api/payment-methods` - Get user's payment methods
- `POST /api/payment-methods` - Add new payment method
- `PUT /api/payment-methods/{id}/set-primary` - Set primary payment method
- `DELETE /api/payment-methods/{id}` - Delete payment method

### Payment Intents
- `POST /api/payment-intents` - Create payment intent
- `POST /api/payment-intents/{id}/confirm` - Confirm payment
- `GET /api/payment-intents/{id}` - Get payment intent status

### Stripe Configuration
- `GET /api/stripe/config` - Get Stripe publishable key

### Webhooks
- `POST /api/webhooks/stripe` - Handle Stripe webhooks

## Production Deployment

### 1. Environment Variables
Update your environment variables with production Stripe keys:
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 2. Webhook Endpoint
Configure webhook endpoint in Stripe dashboard:
```
https://yourdomain.com/api/webhooks/stripe
```

### 3. Security Headers
Ensure these security headers are set:
- `Content-Security-Policy`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Strict-Transport-Security`

### 4. HTTPS Enforcement
All payment pages must use HTTPS in production.

## Monitoring & Maintenance

### 1. Stripe Dashboard
Monitor payments, disputes, and failed payments in your Stripe dashboard.

### 2. Logging
All payment activities are logged for audit purposes.

### 3. Error Handling
Comprehensive error handling with user-friendly messages.

### 4. Testing
Regular testing with Stripe test cards and webhook events.

## Troubleshooting

### Common Issues

**1. "Stripe not loaded" error**
- Ensure `REACT_APP_STRIPE_PUBLISHABLE_KEY` is set correctly
- Check that Stripe keys are valid

**2. Payment method creation fails**
- Verify Stripe secret key is correct
- Check network connectivity to Stripe API

**3. Webhook events not received**
- Ensure webhook endpoint is accessible
- Verify webhook secret is correct
- Check Stripe CLI is forwarding events

**4. Payment confirmation fails**
- Verify payment intent exists
- Check payment method is valid
- Ensure sufficient funds (test cards)

### Debug Mode
Enable debug logging by setting:
```bash
STRIPE_DEBUG=true
```

## Support

For issues with:
- **Stripe Integration**: Check Stripe documentation and dashboard
- **Backend Issues**: Review server logs and API responses
- **Frontend Issues**: Check browser console and network tab
- **Security Concerns**: Review the security guide and implement additional measures

## Next Steps

1. **Test thoroughly** with all test card scenarios
2. **Set up monitoring** for payment success rates
3. **Configure webhooks** for production
4. **Implement additional security** measures as needed
5. **Train team** on payment processing best practices

The integration is now complete with enterprise-grade security and a smooth user experience!
