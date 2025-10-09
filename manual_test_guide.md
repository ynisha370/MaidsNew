# Manual Testing Guide - Complete Workflow

## Prerequisites
1. Backend server running on http://localhost:8000
2. Database seeded with test data
3. Test credentials from seed_database.py

---

## Test Scenario 1: Cleaner Approval Flow

### Step 1: Check Pending Cleaners (Admin)
```bash
# Login as admin first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@maids.com","password":"admin123"}'

# Save the token from response, then:
curl -X GET http://localhost:8000/api/admin/cleaners/pending \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Expected**: Should see Mike Brown and Emily Davis as pending

### Step 2: Approve a Cleaner
```bash
# Use the cleaner ID from previous response
curl -X POST http://localhost:8000/api/admin/cleaners/{CLEANER_ID}/approve \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected**: Cleaner approved, email sent, calendar initialized

### Step 3: Login as Approved Cleaner
```bash
curl -X POST "http://localhost:8000/api/cleaner/login" \
  -d "email=cleaner1@maids.com&password=cleaner123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Expected**: Successful login with token

### Step 4: Try Login as Unapproved Cleaner
```bash
curl -X POST "http://localhost:8000/api/cleaner/login" \
  -d "email=pending1@maids.com&password=cleaner123" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

**Expected**: 403 error with message about pending approval

---

## Test Scenario 2: Booking with Auto-Assignment

### Step 5: Create Customer Booking
```bash
curl -X POST http://localhost:8000/api/bookings/guest \
  -H "Content-Type: application/json" \
  -d '{
    "house_size": "2_bedroom",
    "frequency": "one_time",
    "services": [{"service_id": "standard_cleaning", "service_name": "Standard Cleaning", "price": 150.0}],
    "a_la_carte_services": [],
    "booking_date": "2025-10-15",
    "time_slot": "10:00-12:00",
    "base_price": 150.0,
    "customer": {
      "email": "test@customer.com",
      "first_name": "Test",
      "last_name": "Customer",
      "phone": "+1234567890",
      "address": "123 Test St",
      "city": "Cypress",
      "state": "TX",
      "zip_code": "77433"
    },
    "address": {
      "street": "123 Test St",
      "city": "Cypress",
      "state": "TX",
      "zip_code": "77433"
    }
  }'
```

**Expected**: 
- Booking created
- Cleaner auto-assigned
- Status: "confirmed"
- cleaner_id present in response
- Email sent to assigned cleaner

---

## Test Scenario 3: Job Tracking

### Step 6: View Cleaner's Jobs
```bash
curl -X GET http://localhost:8000/api/cleaner/jobs \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN"
```

**Expected**: List of assigned jobs including the newly created one

### Step 7: Clock In to Job
```bash
curl -X POST http://localhost:8000/api/cleaner/clock-in \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "BOOKING_ID_HERE",
    "latitude": 29.9511,
    "longitude": -95.3698
  }'
```

**Expected**: 
- Status changed to "in_progress"
- Clock-in time recorded
- Location saved

### Step 8: Update ETA
```bash
curl -X POST http://localhost:8000/api/cleaner/update-eta \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "BOOKING_ID_HERE",
    "eta": "30 minutes"
  }'
```

**Expected**: ETA updated, customer notified

### Step 9: Send Message to Customer
```bash
curl -X POST http://localhost:8000/api/cleaner/send-message \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "BOOKING_ID_HERE",
    "message": "On my way! Will arrive shortly."
  }'
```

**Expected**: Message saved, email sent to customer

### Step 10: Clock Out (Complete Job)
```bash
curl -X POST http://localhost:8000/api/cleaner/clock-out \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "BOOKING_ID_HERE",
    "latitude": 29.9511,
    "longitude": -95.3698
  }'
```

**Expected**:
- Status changed to "completed"
- Clock-out time recorded
- Earnings calculated (70% commission = $105)
- Earnings added to cleaner's account

---

## Test Scenario 4: Earnings & Payments

### Step 11: Check Earnings
```bash
curl -X GET http://localhost:8000/api/cleaner/earnings \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN"
```

**Expected**: Total earnings includes payment from completed job

### Step 12: Check Wallet Balance
```bash
curl -X GET http://localhost:8000/api/cleaner/wallet \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN"
```

**Expected**: 
- Balance shows $105 (70% of $150)
- Total earned matches earnings

### Step 13: Check Payment History
```bash
curl -X GET http://localhost:8000/api/cleaner/payments \
  -H "Authorization: Bearer YOUR_CLEANER_TOKEN"
```

**Expected**: Payment record for completed job

---

## Test Scenario 5: Manual Reassignment

### Step 14: Create Another Booking
(Use Step 5 command but with different date)

### Step 15: Manually Reassign Cleaner
```bash
curl -X PATCH http://localhost:8000/api/admin/bookings/{BOOKING_ID} \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cleaner_id": "DIFFERENT_CLEANER_ID"}'
```

**Expected**:
- 3 emails sent:
  1. Old cleaner (job removed)
  2. New cleaner (job assigned)
  3. Customer (cleaner changed)

---

## Test Scenario 6: Admin Reports

### Step 16: View Weekly Report
```bash
curl -X GET http://localhost:8000/api/admin/reports/weekly \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected**:
- Total bookings count
- Revenue totals
- Cleaner completions list
- Completion rate

### Step 17: View Monthly Report
```bash
curl -X GET http://localhost:8000/api/admin/reports/monthly \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected**: Similar to weekly but for the month

---

## Success Criteria Checklist

- [ ] Cleaners can register but not login until approved
- [ ] Admin can see pending cleaners
- [ ] Admin can approve/reject cleaners  
- [ ] Approved cleaners receive email
- [ ] Approved cleaners can login
- [ ] Customer bookings auto-assign to best cleaner
- [ ] Cleaners can view assigned jobs
- [ ] Cleaners can clock in/out
- [ ] Cleaners can update ETA
- [ ] Cleaners can message customers
- [ ] Job completion triggers earnings calculation
- [ ] Earnings appear in cleaner wallet
- [ ] Admin can manually reassign cleaners
- [ ] Reassignment sends notifications to all parties
- [ ] Admin can view reports with cleaner data

---

## Quick Test Commands

### Reset a Cleaner to Pending (for testing)
```bash
# In MongoDB or via script
db.cleaners.updateOne(
  {email: "cleaner1@maids.com"},
  {$set: {is_approved: false, approved_at: null, approved_by: null}}
)
```

### Check Database Directly
```bash
# Connect to MongoDB
mongosh

# Use database
use maidsofcyfair

# Check pending cleaners
db.cleaners.find({is_approved: false})

# Check bookings with assigned cleaners
db.bookings.find({cleaner_id: {$ne: null}})

# Check cleaner availability
db.cleaner_availability.find({cleaner_id: "CLEANER_ID"}).limit(5)
```

---

## Troubleshooting

### Issue: "Not found" on admin endpoints
- Ensure backend server is running
- Check that you're using the correct token
- Verify the endpoint URL is correct

### Issue: Auto-assignment not working
- Check that cleaners have `is_approved: true`
- Verify cleaner_availability records exist
- Ensure time_slot_availability has capacity

### Issue: No earnings showing
- Verify booking status is "completed"
- Check that clock-out was successful
- Query bookings collection for completion data

### Issue: Emails not sending
- Check AWS SES credentials in .env
- Verify email addresses are valid
- Check server logs for email errors

---

## Test Credentials

**Admin:**
- Email: admin@maids.com
- Password: admin123

**Approved Cleaners:**
- cleaner1@maids.com / cleaner123 (Maria Garcia)
- cleaner2@maids.com / cleaner123 (James Wilson)
- cleaner3@maids.com / cleaner123 (Lisa Chen)

**Pending Cleaners:**
- pending1@maids.com / cleaner123 (Mike Brown)
- pending2@maids.com / cleaner123 (Emily Davis)

**Customers:**
- customer1@test.com / password123
- customer2@test.com / password123

---

## Expected Complete Workflow

1. **Registration**: Cleaner signs up → Account created with `is_approved=false`
2. **Pending Email**: Cleaner receives "Application Received" email
3. **Admin Review**: Admin sees cleaner in Pending tab
4. **Approval**: Admin clicks Approve → `is_approved=true`, calendar initialized
5. **Approval Email**: Cleaner receives "Welcome! You're Approved" email
6. **Cleaner Login**: Cleaner can now login successfully
7. **Customer Books**: Customer creates booking
8. **Auto-Assignment**: System finds best cleaner and assigns automatically
9. **Job Email**: Assigned cleaner receives "New Job Assigned" email
10. **Job Start**: Cleaner clocks in → Status: "in_progress"
11. **Communication**: Cleaner updates ETA, sends messages
12. **Job Complete**: Cleaner clocks out → Status: "completed"
13. **Payment**: 70% commission ($105) added to cleaner's wallet
14. **Reports**: Admin sees completed job in reports

---

## Automation Script

For automated testing, run:
```bash
python3 test_complete_workflow.py
```

This will execute all scenarios automatically and provide a summary report.

