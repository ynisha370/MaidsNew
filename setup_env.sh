#!/bin/bash

echo "🔧 Setting up environment variables for Stripe integration..."

# Backend environment setup
echo "📁 Setting up backend environment..."
cd backend

if [ ! -f .env ]; then
    echo "Creating backend .env file..."
    cat > .env << EOF
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

# Google OAuth Configuration
GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback
EOF
    echo "✅ Backend .env file created"
else
    echo "⚠️  Backend .env file already exists"
fi

cd ..

# Frontend environment setup
echo "📁 Setting up frontend environment..."
cd frontend

if [ ! -f .env ]; then
    echo "Creating frontend .env file..."
    cat > .env << EOF
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8000

# Stripe Configuration
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=758684152649-bibv1smukqo58p8q8mk1nuud19edq68a.apps.googleusercontent.com
EOF
    echo "✅ Frontend .env file created"
else
    echo "⚠️  Frontend .env file already exists"
fi

cd ..

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Install dependencies:"
echo "   cd backend && pip install -r requirements.txt"
echo "   cd frontend && npm install"
echo ""
echo "2. Start the servers:"
echo "   Backend: cd backend && python server.py"
echo "   Frontend: cd frontend && npm start"
echo ""
echo "3. Test the integration:"
echo "   python test_stripe_integration.py"
echo ""
echo "🔑 Your Stripe keys are configured:"
echo "   Publishable Key: pk_test_51RzKQdRps3Ulo01CKof4M3aPKgizeI6LEFLs3hvVPj0wBS5rqYqAD2VgmELzDSoFkBJ8MLuLIdNoySlBeBIYWJMt00lL0R0w67"
echo "   Secret Key: sk_test_51RzKQdRps3Ulo01CBYdM3Yeq7KsXP3remjM3drLFEamLjXPd2troAmutNVBrJ3Y5fVCSaMxGwOaCWgPwHvYqKx8o00KoqztCIz"
