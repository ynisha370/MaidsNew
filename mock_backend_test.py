#!/usr/bin/env python3
"""
Mock Backend for Testing (No MongoDB Required)
=============================================

This script creates a simple mock backend that returns fake data
for testing the cleaner dashboard interface without MongoDB.
"""

import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timedelta
import bcrypt

# Mock data
MOCK_USERS = {
    "cleaner@maids.com": {
        "id": "demo_cleaner_001",
        "email": "cleaner@maids.com",
        "password_hash": bcrypt.hashpw("cleaner@123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "first_name": "Demo",
        "last_name": "Cleaner",
        "phone": "555-0123",
        "role": "cleaner",
        "address": {
            "street": "123 Demo Street",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77001"
        },
        "experience_years": 3,
        "hourly_rate": 25.0,
        "specializations": ["Deep cleaning", "Move-in/out", "Post-construction"],
        "languages": ["English", "Spanish"],
        "certifications": ["OSHA Certified"],
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "555-0987",
        "emergency_contact_relationship": "Spouse",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}

MOCK_BOOKINGS = [
    {
        "id": "demo_booking_001",
        "user_id": "demo_customer_001",
        "cleaner_id": "demo_cleaner_001",
        "date": "2024-12-20",
        "start_time": "09:00",
        "end_time": "11:00",
        "status": "confirmed",
        "total_amount": 150.0,
        "duration_hours": 2,
        "address": "456 Customer Ave, Houston, TX 77002",
        "special_instructions": "Please bring extra cleaning supplies for deep cleaning.",
        "services": [
            {"name": "Deep Cleaning", "price": 100.0},
            {"name": "Bathroom Sanitization", "price": 50.0}
        ],
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T10:00:00Z"
    },
    {
        "id": "demo_booking_002",
        "user_id": "demo_customer_002",
        "cleaner_id": "demo_cleaner_001",
        "date": "2024-12-21",
        "start_time": "14:00",
        "end_time": "16:00",
        "status": "in_progress",
        "total_amount": 100.0,
        "duration_hours": 2,
        "address": "789 Oak Street, Houston, TX 77003",
        "special_instructions": "Regular maintenance cleaning.",
        "services": [
            {"name": "Standard Cleaning", "price": 80.0},
            {"name": "Kitchen Deep Clean", "price": 20.0}
        ],
        "created_at": "2024-12-02T14:00:00Z",
        "updated_at": "2024-12-02T14:00:00Z",
        "clock_in_time": "2024-12-21T14:00:00Z"
    },
    {
        "id": "demo_booking_003",
        "user_id": "demo_customer_003",
        "cleaner_id": "demo_cleaner_001",
        "date": "2024-12-19",
        "start_time": "10:00",
        "end_time": "12:00",
        "status": "completed",
        "total_amount": 120.0,
        "duration_hours": 2,
        "address": "321 Pine Road, Houston, TX 77004",
        "special_instructions": "Move-out cleaning required.",
        "services": [
            {"name": "Move-out Cleaning", "price": 120.0}
        ],
        "created_at": "2024-12-01T09:00:00Z",
        "updated_at": "2024-12-19T12:00:00Z",
        "clock_in_time": "2024-12-19T10:00:00Z",
        "clock_out_time": "2024-12-19T12:00:00Z"
    }
]

app = FastAPI(title="Mock Cleaner API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@app.post("/api/auth/login")
async def login(user_data: dict):
    """Mock login endpoint"""
    email = user_data.get("email")
    password = user_data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    user = MOCK_USERS.get(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Return user data without password
    user_response = {k: v for k, v in user.items() if k != "password_hash"}

    return {
        "access_token": "mock_token_12345",
        "user": user_response
    }

@app.get("/api/cleaner/jobs")
async def get_cleaner_jobs(status: str = None, date_range: str = None):
    """Mock get cleaner jobs endpoint"""
    return MOCK_BOOKINGS

@app.post("/api/cleaner/clock-in/{job_id}")
async def clock_in_job(job_id: str):
    """Mock clock in endpoint"""
    return {"message": "Clocked in successfully"}

@app.post("/api/cleaner/clock-out/{job_id}")
async def clock_out_job(job_id: str):
    """Mock clock out endpoint"""
    return {"message": "Clocked out successfully"}

@app.post("/api/cleaner/update-eta/{job_id}")
async def update_eta(job_id: str, eta_data: dict):
    """Mock update ETA endpoint"""
    return {"message": "ETA updated successfully"}

@app.get("/api/available-dates")
async def get_available_dates():
    """Mock available dates endpoint"""
    today = datetime.now().date()
    dates = []
    for i in range(30):
        check_date = today + timedelta(days=i)
        dates.append(check_date.strftime('%Y-%m-%d'))
    return dates

@app.get("/api/cleaner/availability/{date}")
async def check_cleaner_availability(date: str):
    """Mock availability check endpoint"""
    return {
        "date": date,
        "has_available_slots": True,
        "available_slots_count": 6,
        "cleaner_has_booking": False,
        "cleaner_booking_count": 0,
        "is_available": True
    }

@app.get("/api/cleaner/today-jobs")
async def get_today_jobs():
    """Mock today jobs endpoint"""
    today = datetime.now().date().strftime('%Y-%m-%d')
    return [booking for booking in MOCK_BOOKINGS if booking["date"] == today]

@app.get("/api/cleaner/upcoming-jobs")
async def get_upcoming_jobs():
    """Mock upcoming jobs endpoint"""
    today = datetime.now().date()
    future_bookings = []
    for booking in MOCK_BOOKINGS:
        booking_date = datetime.strptime(booking["date"], '%Y-%m-%d').date()
        if booking_date > today:
            future_bookings.append(booking)
    return future_bookings

@app.get("/api/cleaner/earnings")
async def get_cleaner_earnings():
    """Mock earnings endpoint"""
    return {
        "today": 150.0,
        "thisWeek": 370.0,
        "thisMonth": 1200.0,
        "total": 5400.0
    }

@app.get("/api/cleaner/stats")
async def get_cleaner_stats():
    """Mock stats endpoint"""
    return {
        "completedJobs": 25,
        "totalEarnings": 5400.0,
        "rating": 4.8,
        "onTimeRate": 95
    }

@app.get("/api/cleaner/transactions")
async def get_cleaner_transactions():
    """Mock transactions endpoint"""
    return MOCK_BOOKINGS

@app.get("/api/cleaner/payments")
async def get_cleaner_payments():
    """Mock payments endpoint"""
    return [
        {
            "id": "payment_001",
            "amount": 150.0,
            "type": "Bank Transfer",
            "method": "Direct Deposit",
            "status": "completed",
            "created_at": "2024-12-01T10:00:00Z",
            "processed_at": "2024-12-02T14:00:00Z"
        },
        {
            "id": "payment_002",
            "amount": 200.0,
            "type": "Bank Transfer",
            "method": "Direct Deposit",
            "status": "pending",
            "created_at": "2024-12-15T10:00:00Z"
        }
    ]

@app.post("/api/cleaner/withdraw")
async def withdraw_funds(withdrawal_data: dict):
    """Mock withdraw endpoint"""
    return {"message": "Withdrawal request submitted successfully"}

@app.get("/api/cleaner/wallet-balance")
async def get_wallet_balance():
    """Mock wallet balance endpoint"""
    return {
        "available": 5400.0,
        "pending": 150.0
    }

@app.get("/api/cleaner/wallet-transactions")
async def get_wallet_transactions():
    """Mock wallet transactions endpoint"""
    return [
        {
            "id": "txn_001",
            "type": "job_payment",
            "description": "Payment for job #demo_booking_001",
            "amount": 150.0,
            "status": "completed",
            "created_at": "2024-12-20T11:00:00Z"
        },
        {
            "id": "txn_002",
            "type": "job_payment",
            "description": "Payment for job #demo_booking_002",
            "amount": 100.0,
            "status": "completed",
            "created_at": "2024-12-21T16:00:00Z"
        },
        {
            "id": "txn_003",
            "type": "withdrawal",
            "description": "Bank transfer withdrawal",
            "amount": 200.0,
            "status": "completed",
            "created_at": "2024-12-15T10:00:00Z"
        }
    ]

@app.get("/api/cleaner/payment-methods")
async def get_payment_methods():
    """Mock payment methods endpoint"""
    return [
        {
            "id": "pm_001",
            "name": "Chase Checking",
            "type": "bank",
            "is_default": True
        },
        {
            "id": "pm_002",
            "name": "Visa ****1234",
            "type": "card",
            "is_default": False
        }
    ]

@app.post("/api/cleaner/payment-methods")
async def add_payment_method(payment_data: dict):
    """Mock add payment method endpoint"""
    return {"message": "Payment method added successfully"}

@app.get("/api/cleaner/settings")
async def get_cleaner_settings():
    """Mock get settings endpoint"""
    return {
        "notifications": {
            "job_assignments": True,
            "job_reminders": True,
            "payment_notifications": True,
            "schedule_changes": True
        },
        "profile": {
            "first_name": "Demo",
            "last_name": "Cleaner",
            "phone": "555-0123",
            "email": "cleaner@maids.com"
        },
        "privacy": {
            "show_contact_info": True,
            "allow_marketing": False
        }
    }

@app.post("/api/cleaner/settings")
async def update_cleaner_settings(settings_data: dict):
    """Mock update settings endpoint"""
    return {"message": "Settings updated successfully"}

async def main():
    """Start the mock server"""
    print("Starting Mock Backend Server...")
    print("This provides fake data for testing the cleaner dashboard")
    print("No MongoDB required!")
    print()
    print("Mock endpoints available:")
    print("- POST /api/auth/login")
    print("- GET /api/cleaner/jobs")
    print("- POST /api/cleaner/clock-in/{job_id}")
    print("- POST /api/cleaner/clock-out/{job_id}")
    print("- POST /api/cleaner/update-eta/{job_id}")
    print("- GET /api/available-dates")
    print("- GET /api/cleaner/availability/{date}")
    print("- GET /api/cleaner/today-jobs")
    print("- GET /api/cleaner/upcoming-jobs")
    print("- GET /api/cleaner/earnings")
    print("- GET /api/cleaner/stats")
    print()
    print("Demo credentials:")
    print("Email: cleaner@maids.com")
    print("Password: cleaner@123")
    print()
    print("Start frontend: cd frontend && npm start")
    print("Test login: http://localhost:3000/cleaner/login")
    print()

    config = uvicorn.Config(app, host="localhost", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
