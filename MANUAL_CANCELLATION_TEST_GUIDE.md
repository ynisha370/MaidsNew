# Manual Testing Guide - Cancellation Functionality

## 🎯 Purpose
This guide provides step-by-step instructions for manually testing the newly implemented cancellation functionality in the booking system.

## 🔧 Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend application running on `http://localhost:3000`
3. At least one existing booking in the system
4. Admin user account for testing admin cancellation management

## 📋 Test Scenarios

### Scenario 1: Test Cancellation Button in EditCleaningSelection Component
**Objective**: Verify that the cancellation button appears and functions correctly in the booking edit form

**Steps**:
1. **Login to Customer Portal**
   - Navigate to `http://localhost:3000`
   - Login with existing customer credentials
   - Verify you're on the customer dashboard

2. **Access Edit Cleaning Page**
   - Look for the "Edit Cleaning" button in the dashboard
   - Click on "Edit Cleaning" button
   - Verify you're redirected to `/edit-cleaning` page

3. **Verify Cancellation Button**
   - Look for a red "Cancel Booking" button with an X icon
   - The button should be positioned next to the "Save Changes" button
   - Verify the button has proper styling (red background, white text)

4. **Test Cancellation Button Click**
   - Click the "Cancel Booking" button
   - Verify that a cancellation modal opens
   - The modal should show:
     - Booking details (date, time, frequency, total)
     - Cancellation policy warning
     - Reason input field
     - Submit and Cancel buttons

5. **Test Cancellation Modal**
   - Enter a reason for cancellation (e.g., "Change of plans")
   - Click "Submit Request"
   - Verify success message appears
   - Verify modal closes after submission

### Scenario 2: Test Cancellation Request Processing
**Objective**: Verify that cancellation requests are properly submitted and stored

**Steps**:
1. **Submit Cancellation Request**
   - Follow steps 1-5 from Scenario 1
   - Submit a cancellation request with a valid reason

2. **Verify Request Submission**
   - Check browser console for any errors
   - Verify success toast message appears
   - Check that you're redirected back to dashboard

3. **Test Request Retrieval**
   - Login as admin user
   - Navigate to admin dashboard
   - Look for cancellation management section
   - Verify the submitted request appears in the list

### Scenario 3: Test Admin Cancellation Management
**Objective**: Verify that admins can view and manage cancellation requests

**Steps**:
1. **Access Admin Dashboard**
   - Navigate to `http://localhost:3000/admin`
   - Login with admin credentials
   - Verify you're on the admin dashboard

2. **Navigate to Cancellation Management**
   - Look for "Cancellation Management" or similar tab
   - Click to access cancellation requests

3. **Review Cancellation Request**
   - Verify the request from Scenario 2 appears
   - Check that all booking details are displayed
   - Verify customer information is shown
   - Check that the reason is displayed

4. **Test Admin Actions**
   - Try to approve the cancellation request
   - Try to reject the cancellation request
   - Verify appropriate actions are available

### Scenario 4: Test CreateBookingForm Cancellation (Admin)
**Objective**: Verify that the CreateBookingForm component supports cancellation for existing bookings

**Steps**:
1. **Access Admin Dashboard**
   - Login as admin
   - Navigate to admin dashboard

2. **Create Booking for Customer**
   - Go to Customers tab
   - Select a customer
   - Click "Create Booking" button
   - Fill out the booking form
   - Submit the booking

3. **Test Edit Booking with Cancellation**
   - Find the created booking
   - Click to edit the booking
   - Verify that if it's an existing booking, a "Cancel Booking" button appears
   - Test the cancellation functionality

### Scenario 5: Test Error Handling
**Objective**: Verify that the system handles errors gracefully

**Steps**:
1. **Test Without Authentication**
   - Try to access `/edit-cleaning` without logging in
   - Verify you're redirected to login page

2. **Test With Invalid Data**
   - Submit cancellation request without reason
   - Verify error message appears
   - Verify form doesn't submit

3. **Test Network Errors**
   - Disconnect internet temporarily
   - Try to submit cancellation request
   - Verify error handling works

### Scenario 6: Test UI/UX
**Objective**: Verify that the cancellation functionality has good user experience

**Steps**:
1. **Visual Design**
   - Verify cancellation button is clearly visible
   - Check that button styling is consistent with design system
   - Verify proper spacing and alignment

2. **Responsive Design**
   - Test on different screen sizes
   - Verify cancellation button works on mobile
   - Check modal responsiveness

3. **Accessibility**
   - Test keyboard navigation
   - Verify screen reader compatibility
   - Check color contrast

## 🐛 Expected Issues and Troubleshooting

### Common Issues:
1. **Cancellation Button Not Visible**
   - Check if you have an existing booking
   - Verify you're on the correct page (`/edit-cleaning`)
   - Check browser console for JavaScript errors

2. **Modal Not Opening**
   - Check if `CancellationRequestModal` component is imported
   - Verify modal state management
   - Check for JavaScript errors

3. **API Errors**
   - Check backend server is running
   - Verify API endpoints are correct
   - Check authentication tokens

4. **Styling Issues**
   - Verify CSS classes are applied correctly
   - Check for missing imports
   - Verify component structure

## 📊 Test Results Template

```
Test Date: ___________
Tester: ___________
Environment: Local Development

Scenario 1 - EditCleaningSelection Cancellation Button:
[ ] Button visible
[ ] Button clickable
[ ] Modal opens
[ ] Modal displays correctly
[ ] Form submission works

Scenario 2 - Cancellation Request Processing:
[ ] Request submitted successfully
[ ] Success message shown
[ ] Request stored in database

Scenario 3 - Admin Cancellation Management:
[ ] Admin can view requests
[ ] Request details displayed
[ ] Admin actions available

Scenario 4 - CreateBookingForm Cancellation:
[ ] Button appears for existing bookings
[ ] Cancellation functionality works
[ ] Integration with modal works

Scenario 5 - Error Handling:
[ ] Authentication errors handled
[ ] Validation errors shown
[ ] Network errors handled

Scenario 6 - UI/UX:
[ ] Visual design correct
[ ] Responsive design works
[ ] Accessibility features work

Overall Assessment: [ ] PASS [ ] FAIL [ ] NEEDS IMPROVEMENT

Notes:
_________________________________
_________________________________
_________________________________
```

## 🎉 Success Criteria

The cancellation functionality is considered successful if:
- ✅ Cancellation button appears in EditCleaningSelection component
- ✅ Button opens cancellation modal when clicked
- ✅ Modal displays booking details and policy information
- ✅ Users can submit cancellation requests with reasons
- ✅ Admin can view and manage cancellation requests
- ✅ Error handling works properly
- ✅ UI/UX is intuitive and responsive

## 🔧 Development Notes

### Files Modified:
- `frontend/src/components/EditCleaningSelection.js` - Added cancellation button and modal
- `frontend/src/components/CreateBookingForm.js` - Added cancellation support for existing bookings
- `frontend/src/components/CancellationRequestModal.js` - Existing modal component

### Key Features Added:
- Red "Cancel Booking" button with XCircle icon
- Integration with existing CancellationRequestModal
- Proper state management for modal visibility
- Conditional rendering based on existing booking context
- Responsive button layout with proper spacing

### API Endpoints Used:
- `POST /api/cancellation-requests` - Submit cancellation request
- `GET /api/cancellation-requests` - Retrieve user's cancellation requests
- `GET /api/customer/next-appointment` - Get appointment for editing
- `PUT /api/customer/update-cleaning-selection` - Update cleaning selection
