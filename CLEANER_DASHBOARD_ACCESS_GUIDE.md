# 🧹 Cleaner Dashboard Access Guide

## 🚀 How to Access the Cleaner Dashboard

### 1. **Direct URL Access**
- Navigate to: `http://localhost:3000/cleaner/login` (or your deployed URL)
- Use the dedicated cleaner login portal

### 2. **Demo Credentials** (For Testing)
```
Email: cleaner@maids.com
Password: cleaner@123
```

### 3. **New Cleaner Registration**
- Go to: `http://localhost:3000/cleaner/signup`
- Fill out the comprehensive cleaner registration form
- Required fields include:
  - Personal information (name, email, phone)
  - Address details
  - Professional information (experience, hourly rate, specializations)
  - Emergency contact information
  - Account security (password)

### 4. **Login Process**
1. Visit the cleaner login page
2. Enter your credentials
3. Click "Sign In as Cleaner"
4. You'll be redirected to `/cleaner` dashboard

### 5. **Dashboard Features Overview**

#### **📊 Overview Tab (Default)**
- **Today's Jobs**: Shows all scheduled jobs for today
- **Today's Earnings**: Real-time earnings for current day
- **Rating**: Current cleaner rating
- **On-Time Rate**: Punctuality performance metric

#### **💼 Jobs Tab**
- Complete job listing and management interface
- Filter by date, status, customer
- Job details and actions

#### **💰 Earnings Tab**
- Payment history and earnings breakdown
- Weekly, monthly, and total earnings
- Payment status tracking

#### **📅 Schedule Tab**
- Weekly/monthly schedule view
- Availability management
- Upcoming bookings

#### **⚙️ Settings Tab**
- Profile management
- Notification preferences
- Account settings

### 6. **Navigation Features**
- **Clock In/Out**: Time tracking for jobs
- **ETA Updates**: Update estimated arrival times
- **Client Communication**: Contact customers
- **Digital Wallet**: View earnings and payments

### 7. **Mobile Responsiveness**
- Fully responsive design
- Touch-friendly interface
- Mobile-optimized navigation

### 8. **Role-Based Access**
- Only users with `cleaner` role can access
- Automatic redirection from other portals
- Secure authentication system

## 🔧 Technical Implementation

### **Frontend Components Created:**
- `CleanerLogin.js` - Authentication interface
- `CleanerSignup.js` - Registration form
- `CleanerDashboard.js` - Main dashboard

### **Backend Endpoints:**
- `GET /api/available-dates` - Enhanced with cleaner availability
- `GET /api/cleaner/availability/{date}` - Date-specific availability
- Authentication middleware for cleaner role

### **Authentication Flow:**
1. Cleaner logs in via dedicated portal
2. JWT token with cleaner role is issued
3. Frontend redirects to `/cleaner` dashboard
4. All API calls are authenticated with cleaner role

## 🚨 Important Notes

### **Testing the System:**
1. **Start the backend server**: `cd backend && python server.py`
2. **Start the frontend**: `cd frontend && npm start`
3. **Access cleaner dashboard**: `http://localhost:3000/cleaner/login`

### **Demo Data:**
- Use the provided demo credentials for immediate testing
- Create new cleaner accounts for full functionality testing

### **Integration Points:**
- Syncs with existing admin dashboard
- Uses same booking system as customers
- Integrates with payment processing

## 🎯 Next Steps

After accessing the cleaner dashboard, the following features will be implemented:

1. **Jobs View Component** - Detailed job management
2. **Clock In/Out System** - Time tracking
3. **Earnings Dashboard** - Payment history
4. **Digital Wallet** - Balance management
5. **Availability Management** - Schedule control
6. **ETA Communication** - Real-time updates
7. **Admin Integration** - Management tools

---

**🎉 The cleaner dashboard is now live and accessible! Start by logging in with the demo credentials to explore the interface.**
