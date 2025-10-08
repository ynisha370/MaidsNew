# Manual Testing Guide - Cleaner Calendar & Admin Integration

## Prerequisites
1. Backend server running on `http://localhost:5000`
2. MongoDB connection working
3. Admin user exists: admin@maids.com / admin123
4. Cleaner user exists: cleaner@maids.com / cleaner123
5. Test customer exists: test@maids.com / test@maids@1234

## Test Scenarios

### ✅ 1. Admin Authentication
**Endpoint**: `POST /api/auth/login`
```json
{
  "email": "admin@maids.com",
  "password": "admin123"
}
```
**Expected**: Returns access_token and user object

---

### ✅ 2. Cleaner Authentication  
**Endpoint**: `POST /api/cleaner/login?email=cleaner@maids.com&password=cleaner123`
**Expected**: Returns token and cleaner profile

---

### ✅ 3. Admin Views All Bookings
**Endpoint**: `GET /api/admin/bookings`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: List of all bookings

---

### ✅ 4. Admin Views All Cleaners
**Endpoint**: `GET /api/admin/cleaners`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: List of all cleaners

---

### ✅ 5. Customer Creates Booking
**Endpoint**: `POST /api/bookings/no-payment`
**Headers**: `Authorization: Bearer {customer_token}`
```json
{
  "houseSize": "MEDIUM",
  "frequency": "WEEKLY",
  "services": [],
  "aLaCarteServices": [],
  "bookingDate": "2025-10-10",
  "timeSlot": "10:00-12:00",
  "address": {
    "street": "123 Test St",
    "city": "Cypress",
    "state": "TX",
    "zip_code": "77433"
  },
  "specialInstructions": "Test booking"
}
```
**Expected**: Booking created with ID

---

### ✅ 6. Admin Assigns Cleaner to Booking
**Endpoint**: `PATCH /api/admin/bookings/{booking_id}`
**Headers**: `Authorization: Bearer {admin_token}`
```json
{
  "cleaner_id": "{cleaner_id}",
  "status": "confirmed"
}
```
**Expected**: Booking updated with cleaner assignment

---

### ✅ 7. Cleaner Views Assigned Jobs
**Endpoint**: `GET /api/cleaner/jobs`
**Headers**: `Authorization: Bearer {cleaner_token}`
**Expected**: List of jobs assigned to cleaner

---

### ✅ 8. Cleaner Gets Profile
**Endpoint**: `GET /api/cleaner/profile`
**Headers**: `Authorization: Bearer {cleaner_token}`
**Expected**: Cleaner profile data

---

### ✅ 9. Cleaner Clocks In to Job
**Endpoint**: `POST /api/cleaner/clock-in`
**Headers**: `Authorization: Bearer {cleaner_token}`
```json
{
  "jobId": "{booking_id}",
  "latitude": 29.9511,
  "longitude": -95.3698
}
```
**Expected**: Job status changed to "in_progress", clock-in time recorded

---

### ✅ 10. Cleaner Updates ETA
**Endpoint**: `POST /api/cleaner/update-eta`
**Headers**: `Authorization: Bearer {cleaner_token}`
```json
{
  "jobId": "{booking_id}",
  "eta": "15 minutes"
}
```
**Expected**: ETA updated on booking

---

### ✅ 11. Cleaner Sends Message to Client
**Endpoint**: `POST /api/cleaner/send-message`
**Headers**: `Authorization: Bearer {cleaner_token}`
```json
{
  "jobId": "{booking_id}",
  "message": "On my way!"
}
```
**Expected**: Message sent and stored

---

### ✅ 12. Cleaner Clocks Out from Job
**Endpoint**: `POST /api/cleaner/clock-out`
**Headers**: `Authorization: Bearer {cleaner_token}`
```json
{
  "jobId": "{booking_id}",
  "latitude": 29.9511,
  "longitude": -95.3698
}
```
**Expected**: Job status changed to "completed", clock-out time recorded

---

### ✅ 13. Cleaner Views Earnings
**Endpoint**: `GET /api/cleaner/earnings`
**Headers**: `Authorization: Bearer {cleaner_token}`
**Expected**: Total earnings data

---

### ✅ 14. Cleaner Views Wallet
**Endpoint**: `GET /api/cleaner/wallet`
**Headers**: `Authorization: Bearer {cleaner_token}`
**Expected**: Wallet balance and transaction data

---

### ✅ 15. Cleaner Views Payment History
**Endpoint**: `GET /api/cleaner/payments`
**Headers**: `Authorization: Bearer {cleaner_token}`
**Expected**: List of completed payment transactions

---

### ✅ 16. Admin Views Unassigned Jobs
**Endpoint**: `GET /api/admin/calendar/unassigned-jobs`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: List of jobs without cleaner assignment

---

### ✅ 17. Admin Checks Calendar Availability
**Endpoint**: `GET /api/admin/calendar/availability-summary?date=2025-10-10`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: Calendar availability data for date

---

### ✅ 18. Admin Gets Weekly Report
**Endpoint**: `GET /api/admin/reports/weekly`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: Weekly statistics and cleaner completions

---

### ✅ 19. Admin Gets Monthly Report
**Endpoint**: `GET /api/admin/reports/monthly`
**Headers**: `Authorization: Bearer {admin_token}`
**Expected**: Monthly statistics and cleaner completions

---

## Test Flow

### Complete Booking Flow:
1. Customer creates booking → PENDING
2. Admin assigns cleaner → CONFIRMED
3. Cleaner views job → sees assignment
4. Cleaner clocks in → IN_PROGRESS
5. Cleaner updates ETA → client notified
6. Cleaner sends message → client receives
7. Cleaner clocks out → COMPLETED
8. Cleaner sees earnings → payment recorded
9. Admin sees in reports → statistics updated

---

## Verification Checklist

- [ ] All endpoints return proper status codes
- [ ] Authentication works for admin, cleaner, customer
- [ ] Booking status transitions correctly
- [ ] Clock in/out records timestamps
- [ ] ETA updates are saved
- [ ] Messages are stored
- [ ] Earnings calculated correctly (70% commission)
- [ ] Payment history shows completed jobs
- [ ] Admin can view all data
- [ ] Cleaner can only view their own data
- [ ] Calendar integration works
- [ ] Reports show accurate data

---

## Success Criteria

✅ All 19 test scenarios pass
✅ Data persists correctly in MongoDB
✅ Role-based access control working
✅ Real-time updates reflect immediately
✅ No errors in server logs
✅ All integrations working (cleaner ↔ admin ↔ calendar)

---

## Notes

- Payment processing excluded from tests (as requested)
- All tests assume proper database setup
- Tokens must be valid and not expired
- Booking IDs and Cleaner IDs are dynamic

