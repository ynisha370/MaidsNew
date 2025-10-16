# Manual Testing Guide - Customer Management & Recurring Bookings

## 🎯 Purpose
This guide provides step-by-step instructions for manually testing the Customer Management and Recurring Bookings functionality in the admin dashboard.

## 🔧 Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend application running on `http://localhost:3000`
3. Admin user account with proper permissions
4. At least one customer account (registered or guest)

## 📋 Test Scenarios

### Scenario 1: View Customer Management
**Objective**: Verify that admins can view all customers in the dashboard

**Steps**:
1. Login to the admin dashboard
2. Navigate to the "Customers" tab (shortcut: 3)
3. Verify that the customer list loads
4. Check that both registered users and guest customers are displayed
5. Verify customer information includes:
   - Name and email
   - Phone number (if available)
   - Address information
   - Customer type (Guest/Registered)
   - Customer ID

**Expected Result**: 
- Customer list displays all customers
- Information is complete and accurate
- Customer type badges are correct

### Scenario 2: Create Booking for Customer
**Objective**: Test the admin's ability to create bookings for any customer

**Steps**:
1. In the Customers tab, click "Create Booking" for any customer
2. Fill out the booking form:
   - Select house size (e.g., "2000-2500")
   - Choose frequency (e.g., "Weekly")
   - Select services (check "Standard Cleaning")
   - Add rooms (e.g., 3 bedrooms, 2 bathrooms)
   - Select booking date (future date)
   - Choose time slot (e.g., "10:00 AM - 12:00 PM")
   - Verify address information
   - Add special instructions (optional)
3. Review pricing summary
4. Click "Create Booking"

**Expected Result**:
- Booking is created successfully
- Success message appears
- Booking appears in the bookings list
- Pricing is calculated correctly

### Scenario 3: Test Recurring Bookings
**Objective**: Verify that recurring bookings create multiple instances

**Steps**:
1. Create a weekly booking for a customer (as in Scenario 2)
2. Wait 2-3 seconds for recurring bookings to be created
3. Navigate to the "Bookings" tab
4. Filter or search for the customer's bookings
5. Verify that multiple weekly bookings exist for the same customer
6. Check that booking dates are 7 days apart
7. Repeat with bi-weekly and monthly frequencies

**Expected Result**:
- Weekly bookings: 12+ instances created
- Bi-weekly bookings: 12+ instances created  
- Monthly bookings: 12+ instances created
- All dates are correctly calculated
- All bookings have the same customer and service details

### Scenario 4: Test Guest Customer Booking
**Objective**: Verify guest customer booking creation

**Steps**:
1. Create a booking with customer_id: "guest_test@example.com"
2. Use the admin booking creation endpoint
3. Fill out all required fields
4. Submit the booking
5. Check that the guest customer appears in the customer list
6. Verify recurring bookings are created for the guest

**Expected Result**:
- Guest customer booking created successfully
- Guest customer appears in customer list
- Recurring bookings created for guest customer
- Guest customer marked as "Guest" type

### Scenario 5: Test Pricing Calculation
**Objective**: Verify accurate pricing calculations

**Steps**:
1. Create a booking with:
   - House size: "3000-3500"
   - Frequency: "Monthly"
   - Rooms: 4 bedrooms, 3 bathrooms, kitchen, living room
   - A la carte services: Deep cleaning
2. Review the pricing breakdown
3. Verify calculations:
   - Base price for house size and frequency
   - Room pricing (bedrooms × price + bathrooms × price + boolean rooms)
   - A la carte service pricing
   - Total amount

**Expected Result**:
- Base price: $50 (3000-3500 monthly)
- Room pricing: (4 × $12.50) + (3 × $15) + (2 × $8.50) = $50 + $45 + $17 = $112
- A la carte: Deep cleaning price
- Total: Base + Rooms + A la carte

### Scenario 6: Test Error Handling
**Objective**: Verify proper error handling and validation

**Steps**:
1. Try to create a booking with missing required fields
2. Try to create a booking with invalid customer ID
3. Try to create a booking with past date
4. Try to create a booking with invalid time slot
5. Verify error messages are displayed

**Expected Result**:
- Appropriate error messages for each validation failure
- No bookings created with invalid data
- User-friendly error descriptions

## 🔍 Verification Checklist

### Customer Management
- [ ] Customer list loads without errors
- [ ] All customer information is displayed correctly
- [ ] Customer type badges work properly
- [ ] Search/filter functionality works (if implemented)
- [ ] Customer details can be viewed

### Booking Creation
- [ ] Booking form loads with customer data pre-filled
- [ ] All form fields work correctly
- [ ] Service selection works (standard and a la carte)
- [ ] Room selection works (count and boolean)
- [ ] Date and time selection works
- [ ] Address information is pre-filled
- [ ] Pricing calculation is accurate
- [ ] Form validation works properly

### Recurring Bookings
- [ ] Weekly bookings create 12+ instances
- [ ] Bi-weekly bookings create 12+ instances
- [ ] Monthly bookings create 12+ instances
- [ ] Every 3 weeks bookings create 12+ instances
- [ ] Date calculations are correct
- [ ] All instances have same service details
- [ ] All instances have same customer

### Error Handling
- [ ] Missing required fields show validation errors
- [ ] Invalid customer IDs show appropriate errors
- [ ] Past dates are rejected
- [ ] Invalid time slots are rejected
- [ ] Network errors are handled gracefully

## 🐛 Common Issues & Solutions

### Issue: Customer list not loading
**Solution**: Check backend server is running and API endpoints are accessible

### Issue: Recurring bookings not created
**Solution**: Wait 2-3 seconds after booking creation, check server logs

### Issue: Pricing calculation incorrect
**Solution**: Verify room prices and frequency multipliers in backend

### Issue: Form validation not working
**Solution**: Check browser console for JavaScript errors

## 📊 Performance Expectations

- Customer list loading: < 2 seconds
- Booking form loading: < 1 second
- Booking creation: < 3 seconds
- Recurring booking generation: < 5 seconds
- Pricing calculation: < 500ms

## 🎉 Success Criteria

The functionality is working correctly if:
1. ✅ All customers are visible in the admin dashboard
2. ✅ Admins can create bookings for any customer
3. ✅ Recurring bookings create multiple instances
4. ✅ Pricing calculations are accurate
5. ✅ Error handling works properly
6. ✅ Guest customers are handled correctly
7. ✅ All form validations work
8. ✅ Performance meets expectations

---

**Last Updated**: January 15, 2025  
**Version**: 1.0  
**Status**: Ready for Testing
