from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from contextlib import asynccontextmanager
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, date, time, timezone, timedelta
from enum import Enum
import jwt
import bcrypt
import stripe
from stripe import StripeError
import httpx
from services.email_service import email_service
from urllib.parse import quote_plus


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with optimized settings for cloud
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "maidsofcyfair")

# Handle special characters in password for cloud MongoDB
if "qHdDNJMRw8@123" in mongo_url:
    # Replace the problematic password with URL-encoded version
    mongo_url = mongo_url.replace("qHdDNJMRw8@123", "qHdDNJMRw8%40123")
    print(f"Fixed MongoDB URL: {mongo_url}")

# Connection pool settings for cloud MongoDB
max_pool_size = int(os.getenv("MONGO_MAX_POOL_SIZE", "100"))
min_pool_size = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
max_idle_time_ms = int(os.getenv("MONGO_MAX_IDLE_TIME_MS", "30000"))

client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=max_pool_size,
    minPoolSize=min_pool_size,
    maxIdleTimeMS=max_idle_time_ms,
    serverSelectionTimeoutMS=5000,  # 5 second timeout
    connectTimeoutMS=10000,        # 10 second connection timeout
    socketTimeoutMS=20000,         # 20 second socket timeout
    retryWrites=True,              # Enable retryable writes for cloud
    retryReads=True                # Enable retryable reads for cloud
)
db = client[db_name]
# Google Calendar Service
from services.google_calendar_service import GoogleCalendarService
calendar_service = GoogleCalendarService()

# Stripe Configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Servicable zip codes
SERVICABLE_ZIP_CODES = ['77433', '77429', '77095', '77377', '77070', '77065']

def validate_zip_code(zip_code: str) -> bool:
    """Validate if the zip code is in the servicable area"""
    return zip_code in SERVICABLE_ZIP_CODES

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await initialize_database()
    except Exception as e:
        print(f"Warning: Database initialization failed: {str(e)}")
        print("Running in test mode without database")
    try:
        # Try to import and initialize reminder services
        from services.reminder_service import ReminderService

        # Create reminder service instance (only if db is available)
        if 'db' in globals() and db is not None:
            reminder_service = ReminderService(db)
            await reminder_service.initialize_default_templates()
            await reminder_scheduler.start_scheduler()
            print("Reminder service and scheduler initialized successfully")
        else:
            print("Skipping reminder service initialization (no database available)")
    except ImportError as e:
        print(f"Warning: Could not import reminder services: {str(e)}")
    except Exception as e:
        print(f"Error initializing reminder service: {str(e)}")
    yield
    # Shutdown (if needed)
    pass

# Create the main app without a prefix
app = FastAPI(title="Maids of Cyfair Booking System", lifespan=lifespan)

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring database and service status"""
    try:
        # Test database connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
JWT_SECRET = "maids_secret_key_2024"
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Enums
class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed" 
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    CLEANER = "cleaner"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress" 
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ServiceFrequency(str, Enum):
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    EVERY_3_WEEKS = "every_3_weeks"
    BI_WEEKLY = "bi_weekly"
    WEEKLY = "weekly"

class HouseSize(str, Enum):
    SIZE_1000_1500 = "1000-1500"
    SIZE_1500_2000 = "1500-2000"
    SIZE_2000_2500 = "2000-2500"
    SIZE_2500_3000 = "2500-3000"
    SIZE_3000_3500 = "3000-3500"
    SIZE_3500_4000 = "3500-4000"
    SIZE_4000_4500 = "4000-4500"
    SIZE_5000_PLUS = "5000+"
    # Legacy values for backward compatibility
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    # Additional common descriptions found in database
    THREE_BEDROOM = "3_bedroom"
    FOUR_BEDROOM = "4_bedroom"
    FIVE_BEDROOM = "5_bedroom"
    STUDIO = "studio"
    ONE_BEDROOM = "1_bedroom"
    TWO_BEDROOM = "2_bedroom"
    SIX_BEDROOM = "6_bedroom"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"

# Auth Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    password_hash: Optional[str] = None  # Optional for OAuth users
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# Service Models
class Service(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    description: Optional[str] = None
    is_a_la_carte: bool = False
    a_la_carte_price: Optional[float] = None
    duration_hours: Optional[float] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookingService(BaseModel):
    service_id: str
    quantity: int = 1
    special_instructions: Optional[str] = None

class TimeSlot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    time_slot: str
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    apartment: Optional[str] = None

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    customer_id: str
    house_size: HouseSize
    frequency: ServiceFrequency
    rooms: Optional[Dict[str, Any]] = None
    services: List[BookingService]
    a_la_carte_services: List[BookingService] = []
    booking_date: str
    time_slot: str
    base_price: float
    room_price: float = 0.0
    a_la_carte_total: float = 0.0
    total_amount: float
    status: BookingStatus = BookingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    address: Optional[Address] = None
    special_instructions: Optional[str] = None
    cleaner_id: Optional[str] = None
    calendar_event_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration_hours: Optional[float] = None
    assignment_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Cleaner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    first_name: str
    last_name: str
    phone: str
    is_active: bool = True
    rating: float = 5.0
    total_jobs: int = 0
    google_calendar_credentials: Optional[dict] = None
    google_calendar_id: Optional[str] = "primary"
    calendar_integration_enabled: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Custom Calendar Models
class CleanerAvailability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cleaner_id: str
    date: str  # YYYY-MM-DD format
    time_slot: str  # e.g., "09:00-12:00"
    is_available: bool = True
    is_booked: bool = False
    booking_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    event_type: str  # 'booking', 'blocked', 'personal', 'maintenance'
    start_time: datetime
    end_time: datetime
    cleaner_id: Optional[str] = None
    booking_id: Optional[str] = None
    customer_id: Optional[str] = None
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    color: Optional[str] = "#2196F3"  # For calendar display
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TimeSlotAvailability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # YYYY-MM-DD
    time_slot: str  # e.g., "09:00-12:00"
    total_capacity: int = 5  # Number of cleaners available
    booked_count: int = 0
    is_available: bool = True
    is_blocked: bool = False  # Admin can block dates
    blocked_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FAQ(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    answer: str
    category: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Ticket(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    subject: str
    message: str
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Invoice Models
class InvoiceItem(BaseModel):
    service_id: str
    service_name: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: float
    total_price: float

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = Field(default_factory=lambda: f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}")
    booking_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_address: Optional[Address] = None
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float = 0.0825  # 8.25% Texas sales tax
    tax_amount: float
    total_amount: float
    status: InvoiceStatus = InvoiceStatus.DRAFT
    issue_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Calendar Assignment Models
class JobAssignment(BaseModel):
    booking_id: str
    cleaner_id: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

class CalendarTimeSlot(BaseModel):
    start_time: str  # Format: "HH:MM"
    end_time: str
    is_available: bool
    booking_id: Optional[str] = None

# Promo Code Models
class PromoCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    description: Optional[str] = None
    discount_type: DiscountType
    discount_value: float
    minimum_order_amount: Optional[float] = None
    maximum_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    usage_count: int = 0
    usage_limit_per_customer: Optional[int] = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True
    applicable_services: List[str] = []
    applicable_customers: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PromoCodeUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    promo_code_id: str
    customer_id: str
    booking_id: str
    discount_amount: float
    used_at: datetime = Field(default_factory=datetime.utcnow)

class PromoCodeValidation(BaseModel):
    code: str
    subtotal: float

# Stripe Payment Models
class PaymentMethod(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    stripe_payment_method_id: str
    card_brand: str
    last_four: str
    expiry_month: int
    expiry_year: int
    is_primary: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentIntent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    customer_id: str
    stripe_payment_intent_id: str
    amount: int  # Amount in cents
    currency: str = "usd"
    status: str  # requires_payment_method, requires_confirmation, requires_action, processing, requires_capture, canceled, succeeded
    payment_method_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentIntentCreate(BaseModel):
    booking_id: str
    amount: int
    currency: str = "usd"
    payment_method_id: Optional[str] = None

class PaymentMethodCreate(BaseModel):
    card_number: str
    expiry_month: int
    expiry_year: int
    cvc: str
    cardholder_name: str
    is_primary: bool = False

class WebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]
    created: int

# Helper Functions
def prepare_for_mongo(data):
    """Prepare data for MongoDB insertion by converting datetime to ISO strings and enums to their values"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif hasattr(value, 'value'):  # Handle Enum values
                data[key] = value.value
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                data[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
    return data

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_base_price(house_size: HouseSize, frequency: ServiceFrequency) -> float:
    """Calculate base price based on house size and frequency"""
    # Base prices by house size - Updated to match provided pricing table
    size_prices = {
        HouseSize.SIZE_1000_1500: 35,  # 1000-1500 sq ft
        HouseSize.SIZE_1500_2000: 35,  # 1500-2000 sq ft (using same as 1000-1500 for now)
        HouseSize.SIZE_2000_2500: 40,  # 2000-2500 sq ft
        HouseSize.SIZE_2500_3000: 45,  # 2500-3000 sq ft
        HouseSize.SIZE_3000_3500: 50,  # 3000-3500 sq ft
        HouseSize.SIZE_3500_4000: 55,  # 3500-4000 sq ft
        HouseSize.SIZE_4000_4500: 60,  # 4000-4500 sq ft
        HouseSize.SIZE_5000_PLUS: 75   # 5000+ sq ft
    }

    base_price = size_prices.get(house_size, 35)

    # Add $75 additional fee for one-time cleans and move-out cleans
    if frequency == ServiceFrequency.ONE_TIME:
        base_price += 75

    return base_price

def get_dynamic_a_la_carte_price(service: dict, house_size: str) -> float:
    """Dynamically adjust price for size-based services based on house size range.
       For services with size restrictions, automatically select the correct version.
    """
    service_name = service.get("name", "").lower()
    
    # Handle Dust Baseboards
    if "dust baseboards" in service_name:
        if house_size.endswith("+"):
            return 30.0  # > 2500 sq ft
        parts = house_size.split("-")
        if len(parts) == 2:
            try:
                high = int(parts[1])
                return 20.0 if high <= 2500 else 30.0
            except ValueError:
                pass
        return 20.0  # Default to ≤ 2500 sq ft
    
    # Handle Dust Shutters
    elif "dust shutters" in service_name:
        if house_size.endswith("+"):
            return 60.0  # > 2500 sq ft
        parts = house_size.split("-")
        if len(parts) == 2:
            try:
                high = int(parts[1])
                return 40.0 if high <= 2500 else 60.0
            except ValueError:
                pass
        return 40.0  # Default to ≤ 2500 sq ft
    
    # Handle Hand-clean Baseboards
    elif "hand-clean baseboards" in service_name or "hand clean baseboards" in service_name:
        if house_size.endswith("+"):
            return 80.0  # > 2500 sq ft
        parts = house_size.split("-")
        if len(parts) == 2:
            try:
                high = int(parts[1])
                return 60.0 if high <= 2500 else 80.0
            except ValueError:
                pass
        return 60.0  # Default to ≤ 2500 sq ft
    
    # For all other services, return the base price
    return service.get("a_la_carte_price", 0.0)

def get_room_pricing() -> dict:
    """Get room pricing configuration"""
    return {
        # Bedrooms & Bathrooms - Updated to match provided pricing table
        "bedrooms": 8.5,  # per bedroom (all bedrooms)
        "bathrooms": 15.0,  # per bathroom (all bathrooms)
        "halfBathrooms": 10.0,  # per half bathroom

        # Common Areas
        "diningRoom": 8.5,
        "kitchen": 20.0,
        "livingRoom": 8.5,
        "mediaRoom": 8.5,  # Movie Room
        "gameRoom": 8.5,   # 2nd Living room/Game room
        "office": 8.5
    }

def calculate_room_pricing(rooms: dict, frequency: ServiceFrequency) -> float:
    """Calculate pricing based on selected rooms and areas"""
    room_prices = get_room_pricing()
    
    # Frequency multipliers - Updated to match new pricing structure
    frequency_multipliers = {
        ServiceFrequency.ONE_TIME: 1.0,  # One Time Deep Clean/Move Out Cleaning
        ServiceFrequency.MONTHLY: 1.0,   # Monthly
        ServiceFrequency.EVERY_3_WEEKS: 1.0,  # Every 3 weeks
        ServiceFrequency.BI_WEEKLY: 1.0,     # Bi-Weekly
        ServiceFrequency.WEEKLY: 1.0          # Weekly
    }
    
    total_room_price = 0.0
    
    # Calculate pricing for boolean rooms (common areas only)
    boolean_rooms = ["diningRoom", "kitchen", "livingRoom", "mediaRoom", "gameRoom", "office"]
    for room in boolean_rooms:
        if rooms.get(room, False):
            total_room_price += room_prices[room]
    
    # Calculate pricing for count-based rooms (bedrooms and bathrooms)
    count_rooms = ["bedrooms", "bathrooms", "halfBathrooms"]
    for room in count_rooms:
        count = rooms.get(room, 0)
        if count > 0:
            total_room_price += room_prices[room] * count
    
    # Apply frequency multiplier
    multiplier = frequency_multipliers.get(frequency, 1.0)
    return total_room_price * multiplier

def get_room_pricing_breakdown(rooms: dict, frequency: ServiceFrequency) -> dict:
    """Get detailed breakdown of room pricing"""
    room_prices = get_room_pricing()
    
    # Frequency multipliers - Updated to match new pricing structure
    frequency_multipliers = {
        ServiceFrequency.ONE_TIME: 1.0,  # One Time Deep Clean/Move Out Cleaning
        ServiceFrequency.MONTHLY: 1.0,   # Monthly
        ServiceFrequency.EVERY_3_WEEKS: 1.0,  # Every 3 weeks
        ServiceFrequency.BI_WEEKLY: 1.0,     # Bi-Weekly
        ServiceFrequency.WEEKLY: 1.0          # Weekly
    }
    
    multiplier = frequency_multipliers.get(frequency, 1.0)
    breakdown = {}
    
    # Calculate pricing for boolean rooms (common areas only)
    boolean_rooms = ["diningRoom", "kitchen", "livingRoom", "mediaRoom", "gameRoom", "office"]
    for room in boolean_rooms:
        if rooms.get(room, False):
            base_price = room_prices[room]
            final_price = base_price * multiplier
            breakdown[room] = {
                "base_price": base_price,
                "multiplier": multiplier,
                "final_price": final_price
            }
    
    # Calculate pricing for count-based rooms (bedrooms and bathrooms)
    count_rooms = ["bedrooms", "bathrooms", "halfBathrooms"]
    for room in count_rooms:
        count = rooms.get(room, 0)
        if count > 0:
            base_price = room_prices[room]
            final_price = base_price * multiplier
            breakdown[room] = {
                "count": count,
                "base_price_per_unit": base_price,
                "multiplier": multiplier,
                "final_price_per_unit": final_price,
                "total_price": final_price * count
            }
    
    return breakdown

def calculate_job_duration(house_size: HouseSize, services: List[BookingService], a_la_carte_services: List[BookingService]) -> float:
    """Calculate estimated job duration in hours"""
    # Base duration by house size (in hours)
    size_durations = {
        HouseSize.SIZE_1000_1500: 2,
        HouseSize.SIZE_1500_2000: 2.5,
        HouseSize.SIZE_2000_2500: 3,
        HouseSize.SIZE_2500_3000: 3.5,
        HouseSize.SIZE_3000_3500: 4,
        HouseSize.SIZE_3500_4000: 4.5,
        HouseSize.SIZE_4000_4500: 5,
        HouseSize.SIZE_5000_PLUS: 6
    }
    
    base_duration = size_durations.get(house_size, 3)
    
    # Add time for a la carte services (0.5 hour per service)
    additional_duration = len(a_la_carte_services) * 0.5
    
    total_duration = base_duration + additional_duration
    
    # Round up to nearest hour
    return int(total_duration) if total_duration == int(total_duration) else int(total_duration) + 1

def calculate_discount(promo: PromoCode, subtotal: float) -> float:
    """Calculate discount amount with security checks"""
    if promo.discount_type == DiscountType.PERCENTAGE:
        discount = (subtotal * promo.discount_value) / 100
    else:  # FIXED
        discount = promo.discount_value
    
    # Apply maximum discount limit
    if promo.maximum_discount_amount:
        discount = min(discount, promo.maximum_discount_amount)
    
    # Ensure discount doesn't exceed subtotal
    discount = min(discount, subtotal)
    
    # Round to 2 decimal places
    return round(discount, 2)

async def validate_promo_code(code: str, customer_id: str, subtotal: float) -> dict:
    """Comprehensive promo code validation with security checks"""
    # 1. Basic validation
    if not code or len(code.strip()) == 0:
        return {"valid": False, "message": "Promo code is required"}
    
    # 2. Database lookup
    promo = await db.promo_codes.find_one({"code": code.upper()})
    if not promo:
        return {"valid": False, "message": "Invalid promo code"}
    
    # 3. Active status check
    if not promo.get("is_active", False):
        return {"valid": False, "message": "Promo code is not active"}
    
    # 4. Date validation
    now = datetime.now(timezone.utc)
    if promo.get("valid_from") and now < promo["valid_from"]:
        return {"valid": False, "message": "Promo code is not yet valid"}
    
    if promo.get("valid_until") and now > promo["valid_until"]:
        return {"valid": False, "message": "Promo code has expired"}
    
    # 5. Usage limit validation
    if promo.get("usage_limit") and promo.get("usage_count", 0) >= promo["usage_limit"]:
        return {"valid": False, "message": "Promo code usage limit reached"}
    
    # 6. Customer usage limit validation
    customer_usage = await db.promo_code_usage.count_documents({
        "customer_id": customer_id,
        "promo_code_id": promo["id"]
    })
    usage_limit_per_customer = promo.get("usage_limit_per_customer", 1)
    if usage_limit_per_customer and customer_usage >= usage_limit_per_customer:
        return {"valid": False, "message": "You have already used this promo code"}
    
    # 7. Minimum order amount validation
    if promo.get("minimum_order_amount") and subtotal < promo["minimum_order_amount"]:
        return {"valid": False, "message": f"Minimum order amount of ${promo['minimum_order_amount']} required"}
    
    # 8. Customer applicability validation
    if promo.get("applicable_customers") and customer_id not in promo["applicable_customers"]:
        return {"valid": False, "message": "Promo code not applicable to your account"}
    
    # 9. Calculate discount
    # First clean the promo data before creating Pydantic model
    promo_clean = clean_object_for_json(promo)
    promo_obj = PromoCode(**promo_clean)
    discount = calculate_discount(promo_obj, subtotal)

    # Create response with manual serialization
    response_data = {
        "valid": True,
        "promo": promo_clean,
        "discount": float(discount),
        "final_amount": float(subtotal - discount)
    }
    
    # Double-check for any remaining ObjectIds
    def final_clean(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, dict):
            return {k: final_clean(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [final_clean(item) for item in obj]
        else:
            return obj
    
    response_data = final_clean(response_data)
    return response_data

# Stripe Helper Functions
async def create_stripe_customer(user_id: str, email: str, name: str) -> str:
    """Create a Stripe customer and return the customer ID"""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                'user_id': user_id,
                'app': 'maidsofcyfair'
            }
        )
        return customer.id
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create customer: {str(e)}")

async def create_payment_method(customer_id: str, card_data: dict) -> str:
    """Create a Stripe payment method and return the payment method ID"""
    try:
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': card_data['card_number'],
                'exp_month': card_data['expiry_month'],
                'exp_year': card_data['expiry_year'],
                'cvc': card_data['cvc'],
            },
            billing_details={
                'name': card_data['cardholder_name'],
            }
        )
        
        # Attach to customer
        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=customer_id,
        )
        
        return payment_method.id
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create payment method: {str(e)}")

async def create_payment_intent(amount: int, customer_id: str, payment_method_id: str = None) -> dict:
    """Create a Stripe payment intent"""
    try:
        intent_data = {
            'amount': amount,
            'currency': 'usd',
            'customer': customer_id,
            'automatic_payment_methods': {
                'enabled': True,
            },
            'metadata': {
                'app': 'maidsofcyfair'
            }
        }
        
        if payment_method_id:
            intent_data['payment_method'] = payment_method_id
            intent_data['confirmation_method'] = 'manual'
            intent_data['confirm'] = True
        
        payment_intent = stripe.PaymentIntent.create(**intent_data)
        return payment_intent
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to create payment intent: {str(e)}")

async def confirm_payment_intent(payment_intent_id: str) -> dict:
    """Confirm a Stripe payment intent"""
    try:
        payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
        return payment_intent
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to confirm payment: {str(e)}")

async def get_payment_intent(payment_intent_id: str) -> dict:
    """Retrieve a Stripe payment intent"""
    try:
        return stripe.PaymentIntent.retrieve(payment_intent_id)
    except StripeError as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve payment intent: {str(e)}")

def validate_card_number(card_number: str) -> bool:
    """Validate card number using Luhn algorithm"""
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0
    
    # Remove spaces and non-digits
    clean_number = ''.join(filter(str.isdigit, card_number))
    return len(clean_number) >= 13 and len(clean_number) <= 19 and luhn_checksum(clean_number)

def validate_cvc(cvc: str) -> bool:
    """Validate CVC"""
    return cvc.isdigit() and len(cvc) >= 3 and len(cvc) <= 4

def validate_expiry_date(month: int, year: int) -> bool:
    """Validate expiry date"""
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    if year < current_year:
        return False
    if year == current_year and month < current_month:
        return False
    if month < 1 or month > 12:
        return False
    
    return True

def validate_payment_amount(amount: float) -> bool:
    """Validate payment amount"""
    return amount > 0 and amount <= 100000  # Max $1000 for security

def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(input_string, str):
        return str(input_string)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
    for char in dangerous_chars:
        input_string = input_string.replace(char, '')
    
    return input_string.strip()

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid US phone number (10 digits)
    return len(digits_only) == 10

def rate_limit_check(user_id: str, action: str) -> bool:
    """Check if user has exceeded rate limits"""
    # This would integrate with Redis or similar for production
    # For now, we'll implement a simple in-memory check
    import time
    
    # Simple rate limiting - in production, use Redis
    current_time = time.time()
    rate_limit_key = f"{user_id}:{action}"
    
    # This is a placeholder - implement proper rate limiting in production
    return True

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def get_cleaner_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Cleaner access required")
    return current_user

# CORS - Enhanced configuration for Safari compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRFToken",
        "Cache-Control",
        "Pragma",
        "Origin",
        "Referer",
        "User-Agent"
    ],
    expose_headers=["*"],
    max_age=3600
)

# Custom middleware to ensure CORS headers are always present
class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRFToken, Cache-Control, Pragma, Origin, Referer, User-Agent"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
        
        return response

app.add_middleware(CustomCORSMiddleware)

# Static file serving for React production build
frontend_build_path = ROOT_DIR.parent / "frontend" / "build"
if frontend_build_path.exists():
    # Mount static files (CSS, JS, images, etc.)
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / "static")), name="static")
    
    # Mount slides folder for login page images with proper headers
    @app.get("/slides/{filename}")
    @app.head("/slides/{filename}")
    async def serve_slide(filename: str):
        """Serve slide images with proper headers for HTTPS"""
        slide_path = frontend_build_path / "slides" / filename
        if slide_path.exists():
            return FileResponse(
                str(slide_path),
                media_type="image/jpeg" if filename.endswith(('.jpg', '.jpeg')) else "image/png",
                headers={
                    "Cache-Control": "public, max-age=31536000",  # Cache for 1 year
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
        else:
            raise HTTPException(status_code=404, detail="Slide not found")
    
    @app.options("/slides/{filename}")
    async def serve_slide_options(filename: str):
        """Handle CORS preflight requests for slide images"""
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

# Auth endpoints
@api_router.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password)
    )
    
    user_dict = prepare_for_mongo(user.dict())
    await db.users.insert_one(user_dict)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Return user data without password
    user_response = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role": user.role
    }
    
    return AuthResponse(access_token=access_token, user=user_response)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(user_data: UserLogin):
    # Find user by email
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Return user data without password
    user_response = {
        "id": user["id"],
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "phone": user.get("phone"),
        "role": user.get("role", "customer")
    }
    
    return AuthResponse(access_token=access_token, user=user_response)

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": current_user.role
    }

async def get_current_cleaner(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current cleaner user (requires cleaner role)"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.get("role") != "cleaner":
        raise HTTPException(status_code=403, detail="Access denied. Cleaner role required.")

    return User(**user)

# Google OAuth callback endpoint
class GoogleCallbackRequest(BaseModel):
    code: str

# Simple in-memory cache to prevent duplicate code usage
used_codes = set()

@api_router.post("/auth/google/callback", response_model=AuthResponse)
async def google_oauth_callback(request: GoogleCallbackRequest):
    try:
        print(f"Google OAuth callback received code: {request.code[:10]}...")
        print(f"Using redirect URI: {GOOGLE_REDIRECT_URI}")
        
        # Check if code has already been used
        if request.code in used_codes:
            raise HTTPException(status_code=400, detail="Authorization code has already been used")
        
        # Mark code as used
        used_codes.add(request.code)
        
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": request.code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI
        }
        
        print(f"Token exchange request: {token_data}")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            print(f"Token response status: {token_response.status_code}")
            print(f"Token response: {token_response.text}")
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_response.text}")
            
            token_info = token_response.json()
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            google_user = user_response.json()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": google_user["email"]})
        
        if existing_user:
            print(f"Existing user found: {existing_user['email']}")
            # User exists, update with Google ID if not already set
            if not existing_user.get("google_id"):
                await db.users.update_one(
                    {"email": google_user["email"]}, 
                    {"$set": {"google_id": google_user["id"], "updated_at": datetime.now(timezone.utc)}}
                )
                existing_user["google_id"] = google_user["id"]
            user = existing_user
        else:
            print(f"Creating new user: {google_user['email']}")
            # Create new user
            user_data = {
                "id": str(uuid.uuid4()),
                "email": google_user["email"],
                "first_name": google_user.get("given_name", ""),
                "last_name": google_user.get("family_name", ""),
                "phone": None,
                "role": "customer",
                "password_hash": None,  # No password for OAuth users
                "google_id": google_user["id"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            print(f"Inserting user data: {user_data}")
            result = await db.users.insert_one(user_data)
            print(f"User inserted with ID: {result.inserted_id}")
            user = user_data
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        # Return user data
        user_response = {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user.get("phone"),
            "role": user.get("role", "customer")
        }
        
        return AuthResponse(access_token=access_token, user=user_response)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@api_router.get("/auth/google/callback")
async def google_oauth_callback_get(code: str = None, error: str = None, state: str = None):
    """Handle Google OAuth callback via GET request (direct redirect from Google)"""
    try:
        print(f"Google OAuth GET callback received - code: {code[:10] if code else 'None'}..., error: {error}, state: {state}")
        
        if error:
            raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
        
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code received from Google")
        
        # Check if code has already been used
        if code in used_codes:
            raise HTTPException(status_code=400, detail="Authorization code has already been used")
        
        # Mark code as used
        used_codes.add(code)
        
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI
        }
        
        print(f"Token exchange request: {token_data}")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            print(f"Token response status: {token_response.status_code}")
            print(f"Token response: {token_response.text}")
            
            if token_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_response.text}")
            
            token_info = token_response.json()
        
        # Get user info from Google
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        
        async with httpx.AsyncClient() as client:
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            google_user = user_response.json()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": google_user["email"]})
        
        if existing_user:
            print(f"Existing user found: {existing_user['email']}")
            user = existing_user
        else:
            print(f"Creating new user for: {google_user['email']}")
            user_data = {
                "id": str(ObjectId()),
                "email": google_user["email"],
                "first_name": google_user.get("given_name", ""),
                "last_name": google_user.get("family_name", ""),
                "phone": "",
                "role": "customer",
                "google_id": google_user["id"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            print(f"Inserting user data: {user_data}")
            result = await db.users.insert_one(user_data)
            print(f"User inserted with ID: {result.inserted_id}")
            user = user_data
        
        # Create access token
        access_token = create_access_token(data={"sub": user["id"]})
        
        # Return user data
        user_response = {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user.get("phone"),
            "role": user.get("role", "customer")
        }
        
        # For GET requests, we need to redirect to frontend with the token
        # This is a simplified approach - in production you might want to use a more secure method
        frontend_url = f"http://localhost:3000/auth/google/callback?token={access_token}&user={user_response['email']}"
        
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=frontend_url)
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

# Promo Code endpoints
@api_router.post("/validate-promo-code")
async def validate_promo_code_endpoint(validation_data: PromoCodeValidation, current_user: User = Depends(get_current_user)):
    """Validate and calculate discount for a promo code"""
    result = await validate_promo_code(
        validation_data.code, 
        current_user.id, 
        validation_data.subtotal
    )
    return result

# Admin Promo Code Management
def clean_object_for_json(obj):
    """Recursively clean objects for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: clean_object_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_object_for_json(item) for item in obj]
    else:
        return obj

class ObjectIdEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles ObjectId serialization"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@api_router.get("/admin/promo-codes", response_model=List[PromoCode])
async def get_promo_codes(admin_user: User = Depends(get_admin_user)):
    """Get all promo codes with usage statistics"""
    promos = await db.promo_codes.find().sort("created_at", -1).to_list(1000)
    # Convert ObjectId to string for JSON serialization
    clean_promos = []
    for promo in promos:
        promo_clean = clean_object_for_json(promo)
        clean_promos.append(PromoCode(**promo_clean))
    return clean_promos

@api_router.post("/admin/promo-codes", response_model=PromoCode)
async def create_promo_code(promo_data: dict, admin_user: User = Depends(get_admin_user)):
    """Create a new promo code"""
    # Validate required fields
    if not promo_data.get("code") or not promo_data.get("discount_value"):
        raise HTTPException(status_code=400, detail="Code and discount value are required")
    
    # Check if code already exists
    existing = await db.promo_codes.find_one({"code": promo_data["code"].upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Promo code already exists")
    
    # Set default values for optional fields
    promo_data.setdefault("usage_limit_per_customer", 1)
    promo_data.setdefault("is_active", True)
    promo_data.setdefault("applicable_services", [])
    promo_data.setdefault("applicable_customers", [])
    
    # Convert string values to appropriate types
    if promo_data.get("discount_value"):
        promo_data["discount_value"] = float(promo_data["discount_value"])
    if promo_data.get("minimum_order_amount"):
        promo_data["minimum_order_amount"] = float(promo_data["minimum_order_amount"])
    if promo_data.get("maximum_discount_amount"):
        promo_data["maximum_discount_amount"] = float(promo_data["maximum_discount_amount"])
    if promo_data.get("usage_limit"):
        promo_data["usage_limit"] = int(promo_data["usage_limit"])
    if promo_data.get("usage_limit_per_customer"):
        promo_data["usage_limit_per_customer"] = int(promo_data["usage_limit_per_customer"])
    
    # Convert date strings to datetime objects
    if promo_data.get("valid_from"):
        promo_data["valid_from"] = datetime.fromisoformat(promo_data["valid_from"].replace('Z', '+00:00'))
    if promo_data.get("valid_until"):
        promo_data["valid_until"] = datetime.fromisoformat(promo_data["valid_until"].replace('Z', '+00:00'))
    
    # Create promo code
    promo = PromoCode(**promo_data)
    promo_dict = prepare_for_mongo(promo.dict())
    await db.promo_codes.insert_one(promo_dict)
    return promo

@api_router.put("/admin/promo-codes/{promo_id}", response_model=PromoCode)
async def update_promo_code(promo_id: str, promo_data: dict, admin_user: User = Depends(get_admin_user)):
    """Update a promo code"""
    # Check if promo exists
    existing = await db.promo_codes.find_one({"id": promo_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Update promo code
    promo_data["updated_at"] = datetime.utcnow().isoformat()
    result = await db.promo_codes.update_one(
        {"id": promo_id},
        {"$set": promo_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Return updated promo
    updated_promo = await db.promo_codes.find_one({"id": promo_id})
    promo_clean = clean_object_for_json(updated_promo)
    return PromoCode(**promo_clean)

@api_router.patch("/admin/promo-codes/{promo_id}")
async def toggle_promo_code_status(promo_id: str, update_data: dict, admin_user: User = Depends(get_admin_user)):
    """Toggle promo code active status"""
    result = await db.promo_codes.update_one(
        {"id": promo_id},
        {"$set": {**update_data, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    return {"message": "Promo code updated successfully"}

@api_router.delete("/admin/promo-codes/{promo_id}")
async def delete_promo_code(promo_id: str, admin_user: User = Depends(get_admin_user)):
    """Delete a promo code"""
    result = await db.promo_codes.delete_one({"id": promo_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Also delete related usage records
    await db.promo_code_usage.delete_many({"promo_code_id": promo_id})
    
    return {"message": "Promo code deleted successfully"}

# Services endpoints
@api_router.get("/services", response_model=List[Service])
async def get_services():
    services = await db.services.find().to_list(1000)
    # Handle missing category field by providing a default value
    processed_services = []
    for service in services:
        if 'category' not in service:
            service['category'] = 'general'  # Default category
        processed_services.append(Service(**service))
    return processed_services

@api_router.get("/services/standard", response_model=List[Service])
async def get_standard_services():
    services = await db.services.find({"is_a_la_carte": False}).to_list(1000)
    # Handle missing category field by providing a default value
    processed_services = []
    for service in services:
        if 'category' not in service:
            service['category'] = 'general'  # Default category
        processed_services.append(Service(**service))
    return processed_services

@api_router.get("/services/a-la-carte", response_model=List[Service])
async def get_a_la_carte_services():
    services = await db.services.find({"is_a_la_carte": True}).to_list(1000)
    # Handle missing category field by providing a default value
    processed_services = []
    for service in services:
        if 'category' not in service:
            service['category'] = 'general'  # Default category
        processed_services.append(Service(**service))
    return processed_services

@api_router.get("/pricing/{house_size}/{frequency}")
async def get_pricing(house_size: HouseSize, frequency: ServiceFrequency):
    base_price = get_base_price(house_size, frequency)
    return {"house_size": house_size, "frequency": frequency, "base_price": base_price}

@api_router.get("/room-pricing")
async def get_room_pricing_info():
    """Get room pricing configuration"""
    room_prices = get_room_pricing()
    return {
        "room_prices": room_prices,
        "frequency_multipliers": {
            "ONE_TIME": 1.5,
            "MONTHLY": 1.0,
            "EVERY_3_WEEKS": 0.95,
            "BI_WEEKLY": 0.9,
            "WEEKLY": 0.8
        }
    }

@api_router.post("/calculate-room-pricing")
async def calculate_room_pricing_endpoint(request: dict):
    """Calculate pricing for selected rooms and frequency"""
    rooms = request.get('rooms', {})
    frequency = ServiceFrequency(request.get('frequency', 'MONTHLY'))
    
    total_price = calculate_room_pricing(rooms, frequency)
    
    return {
        "rooms": rooms,
        "frequency": frequency.value,
        "total_price": total_price,
        "breakdown": get_room_pricing_breakdown(rooms, frequency)
    }

# Time slots endpoints
@api_router.get("/time-slots")
async def get_time_slots(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    slots = await db.time_slots.find({"date": date, "is_available": True}).to_list(1000)
    return [TimeSlot(**slot) for slot in slots]

@api_router.get("/available-dates")
async def get_available_dates():
    """Get all dates that have available time slots and available cleaners"""
    # Get the next 30 days for availability checking
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=30)

    available_dates = []

    # Check each date for availability
    for i in range(30):
        check_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')

        # Count available time slots for this date
        available_slots = await db.time_slots.count_documents({
            "date": check_date,
            "is_available": True
        })

        # Check if there are cleaners available on this date
        # For now, we assume at least one cleaner is available per day
        # In a more sophisticated system, you'd check actual cleaner schedules
        if available_slots > 0:
            available_dates.append(check_date)

    return available_dates

@api_router.get("/cleaner/availability/{date}")
async def check_cleaner_availability(date: str, current_user: User = Depends(get_current_cleaner)):
    """Check if cleaners are available on a specific date"""
    try:
        # Count available time slots for this date
        available_slots = await db.time_slots.count_documents({
            "date": date,
            "is_available": True
        })

        # Check if current cleaner has any bookings on this date
        cleaner_bookings = await db.bookings.count_documents({
            "cleaner_id": current_user.id,
            "date": date,
            "status": {"$in": ["confirmed", "in_progress"]}
        })

        return {
            "date": date,
            "has_available_slots": available_slots > 0,
            "available_slots_count": available_slots,
            "cleaner_has_booking": cleaner_bookings > 0,
            "cleaner_booking_count": cleaner_bookings,
            "is_available": available_slots > 0 and cleaner_bookings == 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")

# Cleaner job management endpoints
@api_router.get("/cleaner/jobs")
async def get_cleaner_jobs(
    current_user: User = Depends(get_current_cleaner),
    status: str = Query(None, description="Filter by job status"),
    date_range: str = Query(None, description="Filter by date range: today, tomorrow, week, month")
):
    """Get jobs assigned to the current cleaner"""
    try:
        # Build query for bookings
        query = {"cleaner_id": current_user.id}

        # Apply status filter
        if status and status != "all":
            query["status"] = status

        # Apply date range filter
        if date_range and date_range != "all":
            today = datetime.now().date()
            if date_range == "today":
                query["date"] = today.strftime('%Y-%m-%d')
            elif date_range == "tomorrow":
                tomorrow = today + timedelta(days=1)
                query["date"] = tomorrow.strftime('%Y-%m-%d')
            elif date_range == "week":
                week_end = today + timedelta(days=7)
                query["date"] = {"$gte": today.strftime('%Y-%m-%d'), "$lte": week_end.strftime('%Y-%m-%d')}
            elif date_range == "month":
                month_end = today + timedelta(days=30)
                query["date"] = {"$gte": today.strftime('%Y-%m-%d'), "$lte": month_end.strftime('%Y-%m-%d')}

        # Get bookings with customer details
        bookings = await db.bookings.find(query).sort("date", 1).to_list(1000)

        # Enhance bookings with customer information
        enhanced_bookings = []
        for booking in bookings:
            # Get customer details
            customer = await db.users.find_one({"id": booking.get("user_id")})
            if customer:
                booking["customer_name"] = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                booking["customer_email"] = customer.get("email", "")
                booking["customer_phone"] = customer.get("phone", "")

            enhanced_bookings.append(booking)

        return enhanced_bookings

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")

@api_router.post("/cleaner/clock-in/{job_id}")
async def clock_in_job(job_id: str, current_user: User = Depends(get_current_cleaner)):
    """Clock in for a job"""
    try:
        # Find the booking
        booking = await db.bookings.find_one({"id": job_id, "cleaner_id": current_user.id})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")

        if booking.get("status") != "confirmed":
            raise HTTPException(status_code=400, detail="Can only clock in for confirmed jobs")

        # Update booking status to in_progress
        await db.bookings.update_one(
            {"id": job_id},
            {"$set": {
                "status": "in_progress",
                "clock_in_time": datetime.now(),
                "updated_at": datetime.now()
            }}
        )

        return {"message": "Clocked in successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clocking in: {str(e)}")

@api_router.post("/cleaner/clock-out/{job_id}")
async def clock_out_job(job_id: str, current_user: User = Depends(get_current_cleaner)):
    """Clock out from a job"""
    try:
        # Find the booking
        booking = await db.bookings.find_one({"id": job_id, "cleaner_id": current_user.id})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")

        if booking.get("status") != "in_progress":
            raise HTTPException(status_code=400, detail="Can only clock out from in-progress jobs")

        # Update booking status to completed
        await db.bookings.update_one(
            {"id": job_id},
            {"$set": {
                "status": "completed",
                "clock_out_time": datetime.now(),
                "updated_at": datetime.now()
            }}
        )

        return {"message": "Clocked out successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clocking out: {str(e)}")

@api_router.post("/cleaner/update-eta/{job_id}")
async def update_eta(job_id: str, eta_data: dict, current_user: User = Depends(get_current_cleaner)):
    """Update ETA for a job"""
    try:
        eta = eta_data.get("eta")
        if not eta:
            raise HTTPException(status_code=400, detail="ETA time is required")

        # Find the booking
        booking = await db.bookings.find_one({"id": job_id, "cleaner_id": current_user.id})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")

        # Update ETA
        await db.bookings.update_one(
            {"id": job_id},
            {"$set": {
                "eta": eta,
                "updated_at": datetime.now()
            }}
        )

        return {"message": "ETA updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating ETA: {str(e)}")

# Booking endpoints
@api_router.post("/bookings/guest")
async def create_guest_booking(booking_data: dict):
    """Create a booking for guest users (no authentication required)"""
    return await create_booking_internal(booking_data, is_guest=True)

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: dict, current_user: User = Depends(get_current_user)):
    """Create a booking for authenticated users"""
    return await create_booking_internal(booking_data, current_user=current_user, is_guest=False)

async def create_booking_internal(booking_data: dict, current_user: User = None, is_guest: bool = False):
    # Validate zip code - handle both nested and flat data structures
    if 'customer' in booking_data and 'zip_code' in booking_data['customer']:
        customer_zip_code = booking_data['customer']['zip_code']
    elif 'zip_code' in booking_data:
        customer_zip_code = booking_data['zip_code']
    else:
        raise HTTPException(status_code=400, detail="ZIP code is required")

    if not customer_zip_code:
        raise HTTPException(status_code=400, detail="ZIP code is required")

    if not validate_zip_code(customer_zip_code):
        raise HTTPException(
            status_code=400,
            detail=f"We currently only service these ZIP codes: {', '.join(SERVICABLE_ZIP_CODES)}"
        )

    # Check availability for the requested date and time
    booking_date = booking_data.get('booking_date') or booking_data.get('date')
    time_slot = booking_data.get('time_slot') or booking_data.get('time')

    if not booking_date or not time_slot:
        raise HTTPException(status_code=400, detail="Booking date and time slot are required")

    # Check if there are available cleaners for this date and time
    availability_response = await get_availability(booking_date, time_slot)
    if not availability_response['available']:
        raise HTTPException(
            status_code=400,
            detail=f"No cleaners available on {booking_date} at {time_slot}. Please choose a different date or time."
        )
    
    # Calculate room-based pricing if rooms are provided
    room_price = 0.0
    if booking_data.get('rooms'):
        room_price = calculate_room_pricing(booking_data['rooms'], ServiceFrequency(booking_data['frequency']))
    
    # Calculate a la carte total
    a_la_carte_total = 0.0
    if booking_data.get('a_la_carte_services'):
        for service_data in booking_data['a_la_carte_services']:
            service = await db.services.find_one({"id": service_data['service_id']})
            if service:
                # Use dynamic pricing for Dust Baseboards based on the booking house size
                dynamic_price = get_dynamic_a_la_carte_price(service, booking_data['house_size'])
                a_la_carte_total += dynamic_price * service_data.get('quantity', 1)
    
    # Calculate subtotal - include base price, room pricing, and a la carte services
    base_price = booking_data['base_price']
    subtotal = base_price + room_price + a_la_carte_total
    
    # Handle promo code if provided
    discount_amount = 0.0
    promo_code_id = None
    if booking_data.get('promo_code'):
        # For guest users, use a temporary customer ID
        customer_id = current_user.id if current_user else f"guest_{booking_data['customer']['email']}"
        
        # Validate promo code
        validation_result = await validate_promo_code(
            booking_data['promo_code'], 
            customer_id, 
            subtotal
        )
        
        if validation_result['valid']:
            discount_amount = validation_result['discount']
            promo_code_id = validation_result['promo']['id']
        else:
            raise HTTPException(status_code=400, detail=validation_result['message'])
    
    # Calculate final total
    final_total = subtotal - discount_amount
    
    # Create booking
    user_id = current_user.id if current_user else None
    customer_id = current_user.id if current_user else f"guest_{booking_data['customer']['email']}"
    
    booking = Booking(
        user_id=user_id,
        customer_id=customer_id,
        house_size=booking_data['house_size'],
        frequency=booking_data['frequency'],
        rooms=booking_data.get('rooms') if booking_data.get('rooms') else None,
        services=[BookingService(**service) for service in booking_data['services']],
        a_la_carte_services=[BookingService(**service) for service in booking_data.get('a_la_carte_services', [])],
        booking_date=booking_data['booking_date'],
        time_slot=booking_data['time_slot'],
        base_price=base_price,
        room_price=room_price,
        a_la_carte_total=a_la_carte_total,
        total_amount=final_total,
        address=Address(**booking_data['address']) if booking_data.get('address') else Address(
            street=booking_data['customer']['address'],
            city=booking_data['customer']['city'],
            state=booking_data['customer']['state'],
            zip_code=booking_data['customer']['zip_code']
        ),
        special_instructions=booking_data.get('special_instructions'),
        estimated_duration_hours=calculate_job_duration(
            HouseSize(booking_data['house_size']),
            [BookingService(**service) for service in booking_data['services']],
            [BookingService(**service) for service in booking_data.get('a_la_carte_services', [])]
        )
    )
    
    booking_dict = prepare_for_mongo(booking.model_dump())
    
    # Add customer information to the booking document for guest customers
    if not current_user:  # Guest booking
        booking_dict['customer'] = {
            'email': booking_data['customer']['email'],
            'first_name': booking_data['customer']['first_name'],
            'last_name': booking_data['customer']['last_name'],
            'phone': booking_data['customer']['phone'],
            'address': booking_data['customer']['address'],
            'city': booking_data['customer']['city'],
            'state': booking_data['customer']['state'],
            'zip_code': booking_data['customer']['zip_code'],
            'is_guest': True
        }
    
    await db.bookings.insert_one(booking_dict)
    
    # Record promo code usage if applicable
    if promo_code_id and discount_amount > 0:
        usage = PromoCodeUsage(
            promo_code_id=promo_code_id,
            customer_id=customer_id,
            booking_id=booking.id,
            discount_amount=discount_amount
        )
        usage_dict = prepare_for_mongo(usage.dict())
        await db.promo_code_usage.insert_one(usage_dict)
        
        # Increment usage count
        await db.promo_codes.update_one(
            {"id": promo_code_id},
            {"$inc": {"usage_count": 1}}
        )
    
    # Mark time slot as unavailable
    await db.time_slots.update_one(
        {"date": booking_data['booking_date'], "time_slot": booking_data['time_slot']},
        {"$set": {"is_available": False}}
    )
    
    # Create payment intent if user is authenticated and has Stripe customer
    if current_user and not is_guest:
        try:
            user = await db.users.find_one({"id": current_user.id})
            stripe_customer_id = user.get('stripe_customer_id')
            
            if stripe_customer_id:
                # Create payment intent for the booking
                amount_cents = int(final_total * 100)  # Convert to cents
                payment_intent = await create_payment_intent(amount_cents, stripe_customer_id)
                
                # Store payment intent ID in booking
                await db.bookings.update_one(
                    {"id": booking.id},
                    {"$set": {"payment_intent_id": payment_intent['id']}}
                )
        except Exception as e:
            # Log error but don't fail the booking creation
            print(f"Failed to create payment intent: {str(e)}")
    
    return booking

@api_router.get("/bookings", response_model=List[Booking])
async def get_user_bookings(current_user: User = Depends(get_current_user)):
    bookings = await db.bookings.find({"user_id": current_user.id}).to_list(1000)
    return [Booking(**booking) for booking in bookings]

@api_router.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking(booking_id: str, current_user: User = Depends(get_current_user)):
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user owns the booking or is admin
    if current_user.role != UserRole.ADMIN and booking.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Booking(**booking)

@api_router.get("/bookings/{booking_id}/summary")
async def get_booking_summary(booking_id: str, current_user: User = Depends(get_current_user)):
    """Get a comprehensive summary of a booking including all items and services checked out"""
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check if user owns the booking or is admin
    if current_user.role != UserRole.ADMIN and booking.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get customer information
    customer_info = None
    if booking.get("customer"):
        customer_info = booking["customer"]
    else:
        # For registered users, get customer info from users collection
        user = await db.users.find_one({"id": booking.get("user_id")})
        if user:
            customer_info = {
                "email": user.get("email"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "phone": user.get("phone"),
                "address": booking.get("address", {}).get("street", "") if booking.get("address") else "",
                "city": booking.get("address", {}).get("city", "") if booking.get("address") else "",
                "state": booking.get("address", {}).get("state", "") if booking.get("address") else "",
                "zip_code": booking.get("address", {}).get("zip_code", "") if booking.get("address") else "",
                "is_guest": False
            }
    
    # Get service details for all booked services
    services_summary = []
    for booking_service in booking.get("services", []):
        service = await db.services.find_one({"id": booking_service["service_id"]})
        if service:
            services_summary.append({
                "id": service["id"],
                "name": service["name"],
                "description": service["description"],
                "base_price": service["base_price"],
                "quantity": booking_service.get("quantity", 1),
                "total_price": service["base_price"] * booking_service.get("quantity", 1),
                "duration_hours": service.get("duration_hours", 0),
                "category": service.get("category", "standard")
            })
    
    # Get a la carte services details
    a_la_carte_summary = []
    for booking_service in booking.get("a_la_carte_services", []):
        service = await db.services.find_one({"id": booking_service["service_id"]})
        if service:
            a_la_carte_summary.append({
                "id": service["id"],
                "name": service["name"],
                "description": service["description"],
                "base_price": service["base_price"],
                "quantity": booking_service.get("quantity", 1),
                "total_price": service["base_price"] * booking_service.get("quantity", 1),
                "duration_hours": service.get("duration_hours", 0),
                "category": service.get("category", "a_la_carte")
            })
    
    # Get room details if available
    rooms_summary = booking.get("rooms", {})
    
    # Calculate pricing breakdown
    pricing_breakdown = {
        "base_price": booking.get("base_price", 0),
        "room_price": booking.get("room_price", 0),
        "a_la_carte_total": booking.get("a_la_carte_total", 0),
        "subtotal": booking.get("base_price", 0) + booking.get("room_price", 0) + booking.get("a_la_carte_total", 0),
        "discount_amount": booking.get("subtotal", 0) - booking.get("total_amount", booking.get("subtotal", 0)),
        "final_total": booking.get("total_amount", 0)
    }
    
    # Compile the complete summary
    summary = {
        "booking_id": booking["id"],
        "booking_details": {
            "status": booking.get("status"),
            "payment_status": booking.get("payment_status"),
            "booking_date": booking.get("booking_date"),
            "time_slot": booking.get("time_slot"),
            "house_size": booking.get("house_size"),
            "frequency": booking.get("frequency"),
            "estimated_duration_hours": booking.get("estimated_duration_hours"),
            "special_instructions": booking.get("special_instructions"),
            "created_at": booking.get("created_at"),
            "updated_at": booking.get("updated_at")
        },
        "customer_information": customer_info,
        "service_address": booking.get("address") if booking.get("address") else {
            "street": customer_info.get("address", "") if customer_info else "",
            "city": customer_info.get("city", "") if customer_info else "",
            "state": customer_info.get("state", "") if customer_info else "",
            "zip_code": customer_info.get("zip_code", "") if customer_info else ""
        },
        "services_booked": services_summary,
        "a_la_carte_services": a_la_carte_summary,
        "rooms_selected": rooms_summary,
        "pricing_breakdown": pricing_breakdown,
        "payment_summary": {
            "total_amount": booking.get("total_amount", 0),
            "payment_status": booking.get("payment_status"),
            "payment_method": "Online"  # This could be enhanced to track actual payment method
        },
        "next_steps": [
            "Confirmation email will be sent shortly",
            "Professional cleaner will be assigned",
            "Cleaner will arrive on scheduled date and time",
            "Service completion and quality check",
            "Follow-up for customer satisfaction"
        ]
    }
    
    return summary

@api_router.get("/bookings/{booking_id}/guest-summary")
async def get_guest_booking_summary(booking_id: str):
    """Get booking summary for guest users (no authentication required)"""
    booking = await db.bookings.find_one({"id": booking_id})
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only allow access to guest bookings or bookings with customer info
    if not booking.get("customer") and not booking.get("customer_id", "").startswith("guest_"):
        raise HTTPException(status_code=403, detail="Access denied - not a guest booking")
    
    # Use the same logic as the authenticated version but with guest customer info
    customer_info = booking.get("customer", {})
    
    # Get service details for all booked services
    services_summary = []
    for booking_service in booking.get("services", []):
        service = await db.services.find_one({"id": booking_service["service_id"]})
        if service:
            services_summary.append({
                "id": service["id"],
                "name": service["name"],
                "description": service["description"],
                "base_price": service["base_price"],
                "quantity": booking_service.get("quantity", 1),
                "total_price": service["base_price"] * booking_service.get("quantity", 1),
                "duration_hours": service.get("duration_hours", 0),
                "category": service.get("category", "standard")
            })
    
    # Get a la carte services details
    a_la_carte_summary = []
    for booking_service in booking.get("a_la_carte_services", []):
        service = await db.services.find_one({"id": booking_service["service_id"]})
        if service:
            a_la_carte_summary.append({
                "id": service["id"],
                "name": service["name"],
                "description": service["description"],
                "base_price": service["base_price"],
                "quantity": booking_service.get("quantity", 1),
                "total_price": service["base_price"] * booking_service.get("quantity", 1),
                "duration_hours": service.get("duration_hours", 0),
                "category": service.get("category", "a_la_carte")
            })
    
    # Get room details if available
    rooms_summary = booking.get("rooms", {})
    
    # Calculate pricing breakdown
    pricing_breakdown = {
        "base_price": booking.get("base_price", 0),
        "room_price": booking.get("room_price", 0),
        "a_la_carte_total": booking.get("a_la_carte_total", 0),
        "subtotal": booking.get("base_price", 0) + booking.get("room_price", 0) + booking.get("a_la_carte_total", 0),
        "discount_amount": booking.get("subtotal", 0) - booking.get("total_amount", booking.get("subtotal", 0)),
        "final_total": booking.get("total_amount", 0)
    }
    
    # Compile the complete summary
    summary = {
        "booking_id": booking["id"],
        "booking_details": {
            "status": booking.get("status"),
            "payment_status": booking.get("payment_status"),
            "booking_date": booking.get("booking_date"),
            "time_slot": booking.get("time_slot"),
            "house_size": booking.get("house_size"),
            "frequency": booking.get("frequency"),
            "estimated_duration_hours": booking.get("estimated_duration_hours"),
            "special_instructions": booking.get("special_instructions"),
            "created_at": booking.get("created_at"),
            "updated_at": booking.get("updated_at")
        },
        "customer_information": customer_info,
        "service_address": booking.get("address") if booking.get("address") else {
            "street": customer_info.get("address", ""),
            "city": customer_info.get("city", ""),
            "state": customer_info.get("state", ""),
            "zip_code": customer_info.get("zip_code", "")
        },
        "services_booked": services_summary,
        "a_la_carte_services": a_la_carte_summary,
        "rooms_selected": rooms_summary,
        "pricing_breakdown": pricing_breakdown,
        "payment_summary": {
            "total_amount": booking.get("total_amount", 0),
            "payment_status": booking.get("payment_status"),
            "payment_method": "Online"
        },
        "next_steps": [
            "Confirmation email will be sent shortly",
            "Professional cleaner will be assigned",
            "Cleaner will arrive on scheduled date and time",
            "Service completion and quality check",
            "Follow-up for customer satisfaction"
        ]
    }
    
    return summary

@api_router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer information by customer ID"""
    # For guest customers, the customer_id is in format "guest_{email}"
    if customer_id.startswith("guest_"):
        # For guest customers, we need to extract the email and look up the booking
        # to get the customer information that was stored during booking creation
        email = customer_id.replace("guest_", "")
        
        # Find the most recent booking for this guest email
        booking = await db.bookings.find_one(
            {"customer_id": customer_id},
            sort=[("created_at", -1)]
        )
        
        if not booking:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Return customer information from the booking
        return {
            "id": customer_id,
            "email": email,
            "first_name": booking.get("customer", {}).get("first_name", ""),
            "last_name": booking.get("customer", {}).get("last_name", ""),
            "phone": booking.get("customer", {}).get("phone", ""),
            "address": booking.get("customer", {}).get("address", ""),
            "city": booking.get("customer", {}).get("city", ""),
            "state": booking.get("customer", {}).get("state", ""),
            "zip_code": booking.get("customer", {}).get("zip_code", ""),
            "is_guest": True
        }
    else:
        # For registered users, look up in the users collection
        user = await db.users.find_one({"id": customer_id})
        if not user:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "id": user["id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "phone": user.get("phone", ""),
            "address": "",  # Address would be stored in bookings
            "city": "",
            "state": "",
            "zip_code": "",
            "is_guest": False
        }

@api_router.get("/customer/next-appointment")
async def get_next_appointment(current_user: User = Depends(get_current_user)):
    """Get the next upcoming appointment for the current customer"""
    # Find the next upcoming booking for this customer
    next_booking = await db.bookings.find_one(
        {
            "customer_id": current_user.id,
            "booking_date": {"$gte": datetime.now().strftime("%Y-%m-%d")},
            "status": {"$in": ["pending", "confirmed"]}
        },
        sort=[("booking_date", 1), ("time_slot", 1)]
    )
    
    if not next_booking:
        return {"message": "No upcoming appointments found"}
    
    # Convert ObjectId to string for JSON serialization
    if '_id' in next_booking:
        next_booking['_id'] = str(next_booking['_id'])
    
    return next_booking

@api_router.get("/customer/upcoming-appointments")
async def get_upcoming_appointments(current_user: User = Depends(get_current_user)):
    """Get upcoming appointments for the current customer (next month)"""
    # Get current date and next month's date
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_month = datetime.now() + timedelta(days=30)
    next_month_date = next_month.strftime("%Y-%m-%d")
    
    # Find upcoming bookings for this customer
    upcoming_bookings = await db.bookings.find(
        {
            "customer_id": current_user.id,
            "booking_date": {"$gte": current_date, "$lte": next_month_date},
            "status": {"$in": ["pending", "confirmed"]}
        },
        sort=[("booking_date", 1), ("time_slot", 1)]
    ).to_list(1000)
    
    # Convert ObjectId to string for JSON serialization
    for booking in upcoming_bookings:
        if '_id' in booking:
            booking['_id'] = str(booking['_id'])
    
    return upcoming_bookings

# Customer Payment Methods endpoints
@api_router.get("/customer/payment-methods", response_model=List[PaymentMethod])
async def get_customer_payment_methods(current_user: User = Depends(get_current_user)):
    """Get customer's payment methods"""
    try:
        payment_methods = await db.payment_methods.find({"customer_id": current_user.id}).to_list(length=None)
        return [PaymentMethod(**pm) for pm in payment_methods]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment methods: {str(e)}")

@api_router.post("/customer/payment-methods", response_model=PaymentMethod)
async def create_customer_payment_method(
    payment_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new payment method for the customer"""
    
    # Rate limiting check
    if not rate_limit_check(current_user.id, "create_payment_method"):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Sanitize inputs
    payment_data.cardholder_name = sanitize_input(payment_data.cardholder_name)
    
    # Validate card data
    if not validate_card_number(payment_data.card_number):
        raise HTTPException(status_code=400, detail="Invalid card number")
    
    if not validate_cvc(payment_data.cvc):
        raise HTTPException(status_code=400, detail="Invalid CVC")
    
    if not validate_expiry_date(payment_data.expiry_month, payment_data.expiry_year):
        raise HTTPException(status_code=400, detail="Invalid expiry date")
    
    # Validate cardholder name
    if not payment_data.cardholder_name or len(payment_data.cardholder_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Cardholder name must be at least 2 characters")
    
    # Check for duplicate payment methods
    existing_methods = await db.payment_methods.find({
        "customer_id": current_user.id,
        "last_four": payment_data.card_number[-4:]
    }).to_list(length=None)
    
    if existing_methods:
        raise HTTPException(status_code=400, detail="Payment method with this card already exists")
    
    try:
        # Get or create Stripe customer
        user = await db.users.find_one({"id": current_user.id})
        stripe_customer_id = user.get('stripe_customer_id')
        
        if not stripe_customer_id:
            stripe_customer_id = await create_stripe_customer(
                current_user.id, 
                current_user.email, 
                f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            )
            # Update user with Stripe customer ID
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        
        # Create payment method in Stripe
        stripe_payment_method_id = await create_payment_method(
            stripe_customer_id,
            payment_data.dict()
        )
        
        # Get payment method details from Stripe
        payment_method = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
        card = payment_method.card
        
        # If this is set as primary, unset other primary methods
        if payment_data.is_primary:
            await db.payment_methods.update_many(
                {"customer_id": current_user.id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )
        
        # Create payment method record
        payment_method_record = PaymentMethod(
            customer_id=current_user.id,
            stripe_payment_method_id=stripe_payment_method_id,
            card_brand=card.brand,
            last_four=card.last4,
            expiry_month=card.exp_month,
            expiry_year=card.exp_year,
            is_primary=payment_data.is_primary
        )
        
        payment_method_dict = prepare_for_mongo(payment_method_record.dict())
        await db.payment_methods.insert_one(payment_method_dict)
        
        return payment_method_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment method: {str(e)}")

@api_router.put("/customer/payment-methods/{payment_method_id}/set-primary")
async def set_customer_primary_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Set a payment method as primary for the customer"""
    try:
        # First, unset all other primary payment methods for this customer
        await db.payment_methods.update_many(
            {"customer_id": current_user.id},
            {"$set": {"is_primary": False}}
        )
        
        # Set the specified payment method as primary
        result = await db.payment_methods.update_one(
            {"_id": ObjectId(payment_method_id), "customer_id": current_user.id},
            {"$set": {"is_primary": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        return {"message": "Primary payment method updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update primary payment method: {str(e)}")

@api_router.delete("/customer/payment-methods/{payment_method_id}")
async def delete_customer_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a payment method for the customer"""
    try:
        result = await db.payment_methods.delete_one(
            {"_id": ObjectId(payment_method_id), "customer_id": current_user.id}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        return {"message": "Payment method deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment method: {str(e)}")

# Admin endpoints
@api_router.get("/admin/stats")
async def get_admin_stats(admin_user: User = Depends(get_admin_user)):
    # Get stats from database
    total_bookings = await db.bookings.count_documents({})
    total_revenue = await db.bookings.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]).to_list(1)
    total_cleaners = await db.cleaners.count_documents({"is_active": True})
    open_tickets = await db.tickets.count_documents({"status": {"$ne": "closed"}})
    
    return {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue[0]["total"] if total_revenue else 0,
        "total_cleaners": total_cleaners,
        "open_tickets": open_tickets
    }

@api_router.get("/admin/bookings", response_model=List[Booking])
async def get_all_bookings(admin_user: User = Depends(get_admin_user)):
    try:
        bookings = await db.bookings.find().sort("created_at", -1).to_list(1000)
        print(f"Admin bookings endpoint: Found {len(bookings)} bookings")
        return [Booking(**booking) for booking in bookings]
    except Exception as e:
        print(f"Error in admin bookings endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve bookings: {str(e)}")

@api_router.patch("/admin/bookings/{booking_id}")
async def update_booking(booking_id: str, update_data: dict, admin_user: User = Depends(get_admin_user)):
    result = await db.bookings.update_one(
        {"id": booking_id},
        {"$set": {**update_data, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {"message": "Booking updated successfully"}

@api_router.get("/admin/cleaners", response_model=List[Cleaner])
async def get_cleaners(admin_user: User = Depends(get_admin_user)):
    try:
        cleaners = await db.cleaners.find().to_list(1000)
        print(f"Admin cleaners endpoint: Found {len(cleaners)} cleaners")
        
        # Filter out cleaners with missing required fields
        valid_cleaners = []
        for cleaner in cleaners:
            try:
                # Check if required fields exist
                if cleaner.get('first_name') and cleaner.get('last_name'):
                    valid_cleaners.append(Cleaner(**cleaner))
                else:
                    print(f"Skipping cleaner with missing fields: {cleaner.get('email', 'Unknown')}")
            except Exception as e:
                print(f"Error processing cleaner {cleaner.get('email', 'Unknown')}: {e}")
                
        return valid_cleaners
    except Exception as e:
        print(f"Error in admin cleaners endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cleaners: {str(e)}")

@api_router.post("/admin/cleaners", response_model=Cleaner)
async def create_cleaner(cleaner_data: dict, admin_user: User = Depends(get_admin_user)):
    cleaner = Cleaner(**cleaner_data)
    cleaner_dict = prepare_for_mongo(cleaner.dict())
    await db.cleaners.insert_one(cleaner_dict)
    return cleaner

@api_router.delete("/admin/cleaners/{cleaner_id}")
async def delete_cleaner(cleaner_id: str, admin_user: User = Depends(get_admin_user)):
    result = await db.cleaners.delete_one({"id": cleaner_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cleaner not found")
    return {"message": "Cleaner deleted successfully"}

@api_router.get("/admin/services", response_model=List[Service])
async def get_admin_services(admin_user: User = Depends(get_admin_user)):
    services = await db.services.find().to_list(1000)
    # Handle missing category field by providing a default value
    processed_services = []
    for service in services:
        if 'category' not in service:
            service['category'] = 'general'  # Default category
        processed_services.append(Service(**service))
    return processed_services

@api_router.post("/admin/services", response_model=Service)
async def create_service(service_data: dict, admin_user: User = Depends(get_admin_user)):
    service = Service(**service_data)
    service_dict = prepare_for_mongo(service.dict())
    await db.services.insert_one(service_dict)
    return service

@api_router.delete("/admin/services/{service_id}")
async def delete_service(service_id: str, admin_user: User = Depends(get_admin_user)):
    result = await db.services.delete_one({"id": service_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}

@api_router.get("/admin/faqs", response_model=List[FAQ])
async def get_faqs(admin_user: User = Depends(get_admin_user)):
    faqs = await db.faqs.find().to_list(1000)
    return [FAQ(**faq) for faq in faqs]

@api_router.post("/admin/faqs", response_model=FAQ)
async def create_faq(faq_data: dict, admin_user: User = Depends(get_admin_user)):
    faq = FAQ(**faq_data)
    faq_dict = prepare_for_mongo(faq.dict())
    await db.faqs.insert_one(faq_dict)
    return faq

@api_router.delete("/admin/faqs/{faq_id}")
async def delete_faq(faq_id: str, admin_user: User = Depends(get_admin_user)):
    result = await db.faqs.delete_one({"id": faq_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted successfully"}

@api_router.get("/admin/tickets", response_model=List[Ticket])
async def get_tickets(admin_user: User = Depends(get_admin_user)):
    tickets = await db.tickets.find().sort("created_at", -1).to_list(1000)
    return [Ticket(**ticket) for ticket in tickets]

@api_router.patch("/admin/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, update_data: dict, admin_user: User = Depends(get_admin_user)):
    result = await db.tickets.update_one(
        {"id": ticket_id},
        {"$set": {**update_data, "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {"message": "Ticket updated successfully"}

@api_router.get("/admin/export/bookings")
async def export_bookings(admin_user: User = Depends(get_admin_user)):
    bookings = await db.bookings.find().to_list(1000)
    
    # Convert to CSV-friendly format
    csv_data = []
    for booking in bookings:
        csv_data.append({
            "ID": booking["id"],
            "Customer ID": booking.get("customer_id", ""),
            "Date": booking.get("booking_date", ""),
            "Time": booking.get("time_slot", ""),
            "House Size": booking.get("house_size", ""),
            "Frequency": booking.get("frequency", ""),
            "Amount": booking.get("total_amount", 0),
            "Status": booking.get("status", ""),
            "Cleaner": booking.get("cleaner_id", ""),
            "Created": booking.get("created_at", "")
        })
    
    return {"data": csv_data, "filename": f"bookings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}

# Enhanced Google Calendar Integration Endpoints
@api_router.post("/admin/cleaners/{cleaner_id}/calendar/setup")
async def setup_cleaner_calendar(
    cleaner_id: str, 
    calendar_data: dict, 
    admin_user: User = Depends(get_admin_user)
):
    """Setup Google Calendar integration for a cleaner"""
    try:
        credentials = calendar_data.get('credentials')
        calendar_id = calendar_data.get('calendar_id', 'primary')
        
        if not credentials:
            raise HTTPException(status_code=400, detail="Google Calendar credentials required")
        
        # Validate credentials
        if not calendar_service.validate_credentials(credentials):
            raise HTTPException(status_code=400, detail="Invalid Google Calendar credentials")
        
        # Update cleaner with calendar info
        result = await db.cleaners.update_one(
            {"id": cleaner_id},
            {"$set": {
                "google_calendar_credentials": credentials,
                "google_calendar_id": calendar_id,
                "calendar_integration_enabled": True
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cleaner not found")
        
        return {"message": "Calendar integration setup successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to setup calendar: {str(e)}")

@api_router.get("/admin/cleaners/{cleaner_id}/calendar/events")
async def get_cleaner_calendar_events(
    cleaner_id: str,
    days_ahead: int = 7,
    admin_user: User = Depends(get_admin_user)
):
    """Get calendar events for a cleaner"""
    try:
        # Get cleaner info
        cleaner = await db.cleaners.find_one({"id": cleaner_id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")
        
        if not cleaner.get('calendar_integration_enabled'):
            return {"events": [], "message": "Calendar integration not enabled"}
        
        credentials = cleaner.get('google_calendar_credentials')
        calendar_id = cleaner.get('google_calendar_id', 'primary')
        
        if not credentials:
            return {"events": [], "message": "No calendar credentials found"}
        
        # Get calendar service
        service = calendar_service.create_service_from_credentials_dict(credentials)
        if not service:
            return {"events": [], "message": "Failed to connect to calendar"}
        
        # Get events
        events = calendar_service.get_calendar_events(service, calendar_id, days_ahead)
        
        return {
            "events": events,
            "cleaner_id": cleaner_id,
            "calendar_id": calendar_id,
            "days_ahead": days_ahead
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar events: {str(e)}")

@api_router.get("/admin/calendar/availability-summary")
async def get_availability_summary(
    date: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get availability summary for all cleaners for a specific date"""
    try:
        # Get all active cleaners
        cleaners = await db.cleaners.find({"is_active": True}).to_list(1000)
        
        time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
        
        cleaner_availability = []
        
        for cleaner in cleaners:
            cleaner_data = {
                "cleaner_id": cleaner["id"],
                "cleaner_name": f"{cleaner['first_name']} {cleaner['last_name']}",
                "calendar_enabled": cleaner.get('calendar_integration_enabled', False),
                "slots": {}
            }
            
            if cleaner.get('calendar_integration_enabled') and cleaner.get('google_calendar_credentials'):
                # Check availability for each time slot
                credentials = cleaner['google_calendar_credentials']
                service = calendar_service.create_service_from_credentials_dict(credentials)

                if service:
                    for slot in time_slots:
                        start_time, end_time = slot.split('-')
                        job_date = datetime.fromisoformat(date)
                        start_datetime = datetime.combine(job_date.date(), datetime.strptime(start_time, "%H:%M").time())
                        end_datetime = datetime.combine(job_date.date(), datetime.strptime(end_time, "%H:%M").time())

                        is_available = calendar_service.check_availability(
                            service,
                            cleaner.get('google_calendar_id', 'primary'),
                            start_datetime,
                            end_datetime
                        )

                        # Check for existing jobs in this time slot
                        existing_jobs = await db.bookings.find({
                            "cleaner_id": cleaner["id"],
                            "booking_date": job_date.strftime("%Y-%m-%d"),
                            "time_slot": slot
                        }).to_list(10)

                        cleaner_data["slots"][slot] = {
                            "available": is_available,
                            "existing_jobs": existing_jobs
                        }
                else:
                    # If calendar service failed, mark all as available for testing
                    # In production, you might want to check existing bookings instead
                    for slot in time_slots:
                        # Check for existing jobs in this time slot
                        job_date = datetime.fromisoformat(date)
                        existing_jobs = await db.bookings.find({
                            "cleaner_id": cleaner["id"],
                            "booking_date": job_date.strftime("%Y-%m-%d"),
                            "time_slot": slot
                        }).to_list(10)

                        cleaner_data["slots"][slot] = {
                            "available": True,  # Default to available for testing
                            "existing_jobs": existing_jobs
                        }
            else:
                # If no calendar integration, check database for existing jobs and mark availability as unknown
                for slot in time_slots:
                    start_time, end_time = slot.split('-')
                    job_date = datetime.fromisoformat(date)
                    start_datetime = datetime.combine(job_date.date(), datetime.strptime(start_time, "%H:%M").time())
                    end_datetime = datetime.combine(job_date.date(), datetime.strptime(end_time, "%H:%M").time())

                    existing_jobs = await db.bookings.find({
                        "cleaner_id": cleaner["id"],
                        "booking_date": job_date.strftime("%Y-%m-%d"),
                        "time_slot": slot
                    }).to_list(10)

                    cleaner_data["slots"][slot] = {
                        "available": None,  # Unknown availability for non-calendar users
                        "existing_jobs": existing_jobs
                    }
            
            cleaner_availability.append(cleaner_data)
        
        return {
            "date": date,
            "cleaners": cleaner_availability,
            "time_slots": time_slots
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get availability summary: {str(e)}")

@api_router.post("/admin/calendar/assign-job")
async def assign_job_to_calendar(
    assignment_data: JobAssignment,
    admin_user: User = Depends(get_admin_user)
):
    """Assign a job to a cleaner's calendar with drag-and-drop functionality"""
    try:
        # Get booking details
        booking = await db.bookings.find_one({"id": assignment_data.booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get cleaner details
        cleaner = await db.cleaners.find_one({"id": assignment_data.cleaner_id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")
        
        # Check if cleaner has calendar integration
        if not cleaner.get('calendar_integration_enabled') or not cleaner.get('google_calendar_credentials'):
            raise HTTPException(status_code=400, detail="Cleaner doesn't have calendar integration enabled")
        
        # Get calendar service
        credentials = cleaner['google_calendar_credentials']
        service = calendar_service.create_service_from_credentials_dict(credentials)
        
        if not service:
            # For testing purposes, allow assignment even if calendar service fails
            # In production, you might want to require working calendar integration
            print("Warning: Calendar service unavailable, but allowing assignment for testing")
        
        # Check availability for the requested time
        if service:
            is_available = calendar_service.check_availability(
                service,
                cleaner.get('google_calendar_id', 'primary'),
                assignment_data.start_time,
                assignment_data.end_time
            )
        else:
            # For testing, assume available if service is not available
            is_available = True
        
        if not is_available:
            raise HTTPException(status_code=409, detail="Cleaner is not available during the requested time")
        
        # Create calendar event
        job_data = {
            "job_id": booking["id"],
            "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
            "address": f"{booking.get('address', {}).get('street', '')} {booking.get('address', {}).get('city', '')}",
            "services": f"{booking.get('house_size', '')} - {booking.get('frequency', '')}",
            "amount": booking.get('total_amount', 0),
            "instructions": booking.get('special_instructions', 'None'),
            "start_time": assignment_data.start_time.isoformat(),
            "end_time": assignment_data.end_time.isoformat()
        }
        
        if service:
            event_id = calendar_service.create_job_event(
                service,
                cleaner.get('google_calendar_id', 'primary'),
                job_data
            )
        else:
            # For testing, create a mock event ID
            event_id = f"mock_event_{booking['id']}"
        
        if not event_id:
            # For testing, use a fallback event ID
            event_id = f"fallback_event_{booking['id']}_{datetime.utcnow().isoformat()}"
        
        # Update booking with cleaner assignment and calendar event
        update_data = {
            "cleaner_id": assignment_data.cleaner_id,
            "calendar_event_id": event_id,
            "status": "confirmed",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if assignment_data.notes:
            update_data["assignment_notes"] = assignment_data.notes
        
        await db.bookings.update_one(
            {"id": assignment_data.booking_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Job assigned successfully",
            "booking_id": assignment_data.booking_id,
            "cleaner_id": assignment_data.cleaner_id,
            "calendar_event_id": event_id,
            "start_time": assignment_data.start_time.isoformat(),
            "end_time": assignment_data.end_time.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign job: {str(e)}")

@api_router.get("/admin/calendar/unassigned-jobs")
async def get_unassigned_jobs(admin_user: User = Depends(get_admin_user)):
    """Get all unassigned jobs for drag-and-drop assignment"""
    try:
        # Get bookings without cleaner assignment
        unassigned_bookings = await db.bookings.find({
            "cleaner_id": {"$exists": False},
            "status": {"$in": ["pending", "confirmed"]}
        }).sort("booking_date", 1).to_list(1000)
        
        jobs = []
        for booking in unassigned_bookings:
            jobs.append({
                "id": booking["id"],
                "customer_id": booking.get("customer_id", "")[:8],
                "booking_date": booking.get("booking_date"),
                "time_slot": booking.get("time_slot"),
                "house_size": booking.get("house_size"),
                "frequency": booking.get("frequency"),
                "total_amount": booking.get("total_amount"),
                "estimated_duration_hours": booking.get("estimated_duration_hours", 2),
                "address": booking.get("address", {}),
                "special_instructions": booking.get("special_instructions"),
                "services": booking.get("services", []),
                "a_la_carte_services": booking.get("a_la_carte_services", [])
            })
        
        return {"unassigned_jobs": jobs}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unassigned jobs: {str(e)}")

# Invoice Management Endpoints
@api_router.get("/admin/invoices", response_model=List[Invoice])
async def get_all_invoices(
    status: Optional[InvoiceStatus] = None,
    admin_user: User = Depends(get_admin_user)
):
    """Get all invoices with optional status filter"""
    query = {}
    if status:
        query["status"] = status
    
    invoices = await db.invoices.find(query).sort("created_at", -1).to_list(1000)
    return [Invoice(**invoice) for invoice in invoices]

@api_router.post("/admin/invoices/generate/{booking_id}", response_model=Invoice)
async def generate_invoice_for_booking(
    booking_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Generate invoice for a completed booking"""
    try:
        # Get booking details
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Check if invoice already exists
        existing_invoice = await db.invoices.find_one({"booking_id": booking_id})
        if existing_invoice:
            raise HTTPException(status_code=400, detail="Invoice already exists for this booking")
        
        # Get customer details
        customer = await db.users.find_one({"id": booking["customer_id"]})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get service details
        services = await db.services.find().to_list(1000)
        service_map = {service["id"]: service for service in services}
        
        # Create invoice items
        invoice_items = []
        
        # Add base service
        invoice_items.append(InvoiceItem(
            service_id="base_service",
            service_name=f"{booking['house_size']} - {booking['frequency']} Cleaning",
            description=f"Standard cleaning for {booking['house_size']} sqft home",
            quantity=1,
            unit_price=booking.get("base_price", 0),
            total_price=booking.get("base_price", 0)
        ))
        
        # Add a la carte services
        for a_la_carte in booking.get("a_la_carte_services", []):
            service = service_map.get(a_la_carte["service_id"])
            if service:
                unit_price = service.get("a_la_carte_price", 0)
                quantity = a_la_carte.get("quantity", 1)
                invoice_items.append(InvoiceItem(
                    service_id=service["id"],
                    service_name=service["name"],
                    description=service.get("description", ""),
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity
                ))
        
        # Calculate totals
        subtotal = sum(item.total_price for item in invoice_items)
        tax_rate = 0.0825  # 8.25% Texas sales tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Create invoice
        invoice = Invoice(
            booking_id=booking_id,
            customer_id=booking["customer_id"],
            customer_name=f"{customer['first_name']} {customer['last_name']}",
            customer_email=customer["email"],
            customer_address=Address(**booking["address"]) if booking.get("address") else None,
            items=invoice_items,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total_amount=total_amount,
            status=InvoiceStatus.DRAFT,
            due_date=datetime.utcnow() + timedelta(days=30),  # 30 days from creation
            notes=f"Invoice for cleaning services on {booking.get('booking_date', '')}"
        )
        
        # Save to database
        invoice_dict = prepare_for_mongo(invoice.dict())
        await db.invoices.insert_one(invoice_dict)
        
        return invoice
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice: {str(e)}")

@api_router.patch("/admin/invoices/{invoice_id}")
async def update_invoice_status(
    invoice_id: str,
    update_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update invoice status and other fields"""
    try:
        # Add paid_date if status is being set to paid
        if update_data.get("status") == "paid" and "paid_date" not in update_data:
            update_data["paid_date"] = datetime.utcnow().isoformat()
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        result = await db.invoices.update_one(
            {"id": invoice_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {"message": "Invoice updated successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update invoice: {str(e)}")

@api_router.get("/admin/invoices/{invoice_id}/pdf")
async def generate_invoice_pdf(
    invoice_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Generate PDF for invoice"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from io import BytesIO
        import base64
        from datetime import datetime
        
        # Get invoice details
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # Professional color scheme
        primary_blue = colors.HexColor('#2563eb')  # Professional blue
        light_blue = colors.HexColor('#dbeafe')    # Light blue background
        dark_gray = colors.HexColor('#374151')     # Dark gray text
        light_gray = colors.HexColor('#f3f4f6')    # Light gray background
        
        # Custom styles
        company_style = ParagraphStyle(
            'CompanyStyle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=primary_blue,
            spaceAfter=10,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=dark_gray,
            spaceAfter=20,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=primary_blue,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        client_info_style = ParagraphStyle(
            'ClientInfo',
            parent=styles['Normal'],
            fontSize=11,
            textColor=dark_gray,
            spaceAfter=4,
            fontName='Helvetica'
        )
        
        # Build PDF content
        story = []
        
        # Company Header with Logo
        logo_loaded = False
        try:
            # Try multiple possible paths for the logo
            possible_paths = [
                "../frontend/src/assets/logo.png",
                "frontend/src/assets/logo.png",
                "logo.png"
            ]
            
            logo = None
            for logo_path in possible_paths:
                try:
                    logo = Image(logo_path, width=2*inch, height=2*inch)
                    story.append(logo)
                    logo_loaded = True
                    break
                except:
                    continue
                    
            if not logo_loaded:
                raise Exception("Logo not found in any expected location")
                
            story.append(Spacer(1, 10))
        except Exception as e:
            # Fallback to text if logo not found
            print(f"Logo not found: {e}")
            story.append(Paragraph("Maids of Cy-Fair", company_style))
            story.append(Spacer(1, 10))
        
        # Company Name (if logo is present, this can be smaller)
        if logo_loaded:
            company_name_style = ParagraphStyle(
                'CompanyNameStyle',
                parent=styles['Heading2'],
                fontSize=18,
                textColor=primary_blue,
                spaceAfter=10,
                alignment=1,  # Center alignment
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("Maids of Cy-Fair", company_name_style))
        else:
            # If no logo, use the original large company style
            story.append(Paragraph("Maids of Cy-Fair", company_style))
        
        story.append(Spacer(1, 10))
        
        # Invoice Title and Metadata
        invoice_number = invoice.get('invoice_number', 'N/A')
        invoice_date = invoice.get('issue_date', invoice.get('created_at', datetime.now()))
        if isinstance(invoice_date, str):
            invoice_date = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
        formatted_date = invoice_date.strftime('%B %d, %Y')
        
        story.append(Paragraph(f"Invoice no. #{invoice_number}", invoice_title_style))
        story.append(Paragraph(f"Date: {formatted_date}", client_info_style))
        story.append(Spacer(1, 20))
        
        # Client Information Section
        story.append(Paragraph("Client Information", section_header_style))
        
        # Get customer details
        customer = await db.users.find_one({"id": invoice.get('customer_id')})
        customer_name = invoice.get('customer_name', 'N/A')
        customer_email = invoice.get('customer_email', 'N/A')
        customer_phone = customer.get('phone', 'N/A') if customer else 'N/A'
        customer_address = invoice.get('customer_address', {})
        
        # Format address
        address_lines = []
        if customer_address:
            if customer_address.get('street'):
                address_lines.append(customer_address['street'])
            if customer_address.get('city') and customer_address.get('state'):
                address_lines.append(f"{customer_address['city']}, {customer_address['state']}")
            if customer_address.get('zip_code'):
                address_lines.append(customer_address['zip_code'])
        
        client_info_data = [
            ['Name:', customer_name],
            ['Address:', '\n'.join(address_lines) if address_lines else 'N/A'],
            ['Email:', customer_email],
            ['Phone:', customer_phone]
        ]
        
        client_table = Table(client_info_data, colWidths=[1.5*inch, 4.5*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), light_blue),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_gray),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (1, 0), (1, -1), light_gray),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(client_table)
        story.append(Spacer(1, 20))
        
        # Job Description Section
        story.append(Paragraph("Job Description", section_header_style))
        
        service_data = [['Job Description', 'Total']]
        
        # Add service items
        for item in invoice.get('items', []):
            service_name = item.get('service_name', item.get('description', 'N/A'))
            total_price = item.get('total_price', item.get('amount', 0))
            service_data.append([
                service_name,
                f"${total_price:.2f}"
            ])
        
        service_table = Table(service_data, colWidths=[4.5*inch, 1.5*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), light_gray),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(service_table)
        story.append(Spacer(1, 20))
        
        # Payment Information Section
        story.append(Paragraph("Payment Information", section_header_style))
        
        payment_info_text = "We accept all major debit / credit cards"
        story.append(Paragraph(payment_info_text, client_info_style))
        story.append(Spacer(1, 10))
        
        # Total Amount Due - Prominent Display
        total_amount = invoice.get('total_amount', 0)
        total_style = ParagraphStyle(
            'TotalAmount',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=primary_blue,
            spaceAfter=20,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph(f"Total Amount Due: ${total_amount:.2f}", total_style))
        story.append(Spacer(1, 20))
        
        # Detailed Totals (if needed for transparency)
        totals_data = [
            ['Subtotal:', f"${invoice.get('subtotal', 0):.2f}"],
            ['Tax (8.25%):', f"${invoice.get('tax_amount', 0):.2f}"],
            ['Total:', f"${total_amount:.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('LINEBELOW', (0, -1), (-1, -1), 2, primary_blue),
            ('TEXTCOLOR', (0, 0), (-1, -1), dark_gray),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 30))
        
        # Professional Footer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=primary_blue,
            spaceAfter=8,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        company_address_style = ParagraphStyle(
            'CompanyAddress',
            parent=styles['Normal'],
            fontSize=10,
            textColor=dark_gray,
            spaceAfter=4,
            alignment=1,  # Center alignment
            fontName='Helvetica'
        )
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Maids of Cy-Fair", footer_style))
        story.append(Paragraph("Professional Cleaning Services", company_address_style))
        story.append(Paragraph("Serving the Cy-Fair Area", company_address_style))
        story.append(Paragraph("Phone: (281) 555-0123 | Email: info@maidsofcyfair.com", company_address_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Convert to base64 for response
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        return {
            "message": "PDF generated successfully",
            "invoice_id": invoice_id,
            "pdf_content": pdf_base64,
            "filename": f"invoice_{invoice.get('invoice_number', invoice_id)}.pdf"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@api_router.delete("/admin/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Delete an invoice (only if status is draft)"""
    try:
        # Check invoice status
        invoice = await db.invoices.find_one({"id": invoice_id})
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        if invoice.get("status") != "draft":
            raise HTTPException(status_code=400, detail="Can only delete draft invoices")
        
        result = await db.invoices.delete_one({"id": invoice_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        return {"message": "Invoice deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete invoice: {str(e)}")

# ============================================================================
# CLEANER API ENDPOINTS
# ============================================================================

# Cleaner authentication
@api_router.post("/cleaner/login")
async def cleaner_login(email: str, password: str):
    """Login endpoint for cleaners"""
    try:
        # Find user with cleaner role
        user = await db.users.find_one({"email": email, "role": "cleaner"})
        if not user or not verify_password(password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Find cleaner profile
        cleaner = await db.cleaners.find_one({"email": email})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner profile not found")
        
        # Generate token
        token = create_access_token({"sub": user["id"], "role": "cleaner"})
        
        return {
            "token": token,
            "user": {
                "id": cleaner.get("id"),
                "name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
                "email": cleaner.get("email"),
                "phone": cleaner.get("phone"),
                "rating": cleaner.get("rating", 5.0),
                "completedJobs": cleaner.get("total_jobs", 0),
                "isActive": cleaner.get("is_active", True),
                "createdAt": cleaner.get("created_at", datetime.utcnow()).isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@api_router.post("/cleaner/register")
async def cleaner_register(
    name: str,
    email: str,
    phone: str,
    password: str
):
    """Register a new cleaner"""
    try:
        # Check if email exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user account
        name_parts = name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password_hash=hash_password(password),
            role=UserRole.CLEANER
        )
        await db.users.insert_one(prepare_for_mongo(user.dict()))
        
        # Create cleaner profile
        cleaner = Cleaner(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        await db.cleaners.insert_one(prepare_for_mongo(cleaner.dict()))
        
        # Generate token
        token = create_access_token({"sub": user.id, "role": "cleaner"})
        
        return {
            "token": token,
            "user": {
                "id": cleaner.id,
                "name": name,
                "email": email,
                "phone": phone,
                "rating": 5.0,
                "completedJobs": 0,
                "isActive": True,
                "createdAt": datetime.utcnow().isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@api_router.get("/cleaner/profile")
async def get_cleaner_profile(current_user: User = Depends(get_current_user)):
    """Get cleaner profile information"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    cleaner = await db.cleaners.find_one({"email": current_user.email})
    if not cleaner:
        raise HTTPException(status_code=404, detail="Cleaner profile not found")
    
    return {
        "user": {
            "id": cleaner.get("id"),
            "name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
            "email": cleaner.get("email"),
            "phone": cleaner.get("phone"),
            "rating": cleaner.get("rating", 5.0),
            "completedJobs": cleaner.get("total_jobs", 0),
            "isActive": cleaner.get("is_active", True),
            "createdAt": cleaner.get("created_at", datetime.utcnow()).isoformat()
        }
    }

@api_router.get("/cleaner/jobs")
async def get_cleaner_jobs(current_user: User = Depends(get_current_user)):
    """Get all jobs assigned to the cleaner"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        cleaner = await db.cleaners.find_one({"email": current_user.email})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner profile not found")
        
        # Get all bookings assigned to this cleaner
        bookings = await db.bookings.find({
            "cleaner_id": cleaner.get("id")
        }).sort("booking_date", 1).to_list(1000)
        
        jobs = []
        for booking in bookings:
            # Get customer info
            customer = await db.users.find_one({"id": booking.get("customer_id")})
            customer_name = "Guest Customer"
            customer_phone = ""
            if customer:
                customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
                customer_phone = customer.get("phone", "")
            
            # Parse booking date and time
            booking_date_str = booking.get("booking_date", "")
            time_slot = booking.get("time_slot", "9:00 AM - 12:00 PM")
            
            # Create job object
            job_status = "assigned"
            if booking.get("status") == "completed":
                job_status = "completed"
            elif booking.get("status") == "in_progress":
                job_status = "inProgress"
            elif booking.get("status") == "confirmed":
                job_status = "assigned"
            
            job = {
                "id": booking.get("id"),
                "clientName": customer_name,
                "clientPhone": customer_phone,
                "clientAddress": f"{booking.get('address', {}).get('street', '')} {booking.get('address', {}).get('city', '')} {booking.get('address', {}).get('state', '')} {booking.get('address', {}).get('zip_code', '')}",
                "serviceType": f"{booking.get('house_size', '')} - {booking.get('frequency', '')}",
                "scheduledDate": booking_date_str,
                "scheduledTime": time_slot,
                "price": booking.get("total_amount", 0),
                "status": job_status,
                "tasks": [
                    {"id": "1", "description": "Perform cleaning service", "isCompleted": False}
                ],
                "notes": booking.get("special_instructions", ""),
                "eta": booking.get("eta"),
                "clockInTime": booking.get("clock_in_time"),
                "clockOutTime": booking.get("clock_out_time")
            }
            jobs.append(job)
        
        return {"jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get jobs: {str(e)}")

@api_router.post("/cleaner/clock-in")
async def clock_in(
    jobId: str,
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
):
    """Clock in to a job"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        booking = await db.bookings.find_one({"id": jobId})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update booking with clock in time
        await db.bookings.update_one(
            {"id": jobId},
            {
                "$set": {
                    "clock_in_time": datetime.utcnow().isoformat(),
                    "clock_in_location": {"lat": latitude, "lng": longitude},
                    "status": "in_progress",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Get updated booking
        updated_booking = await db.bookings.find_one({"id": jobId})
        
        return {
            "message": "Clocked in successfully",
            "job": {
                "id": updated_booking.get("id"),
                "status": "inProgress",
                "clockInTime": updated_booking.get("clock_in_time")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clock in failed: {str(e)}")

@api_router.post("/cleaner/clock-out")
async def clock_out(
    jobId: str,
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
):
    """Clock out from a job"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        booking = await db.bookings.find_one({"id": jobId})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update booking with clock out time
        await db.bookings.update_one(
            {"id": jobId},
            {
                "$set": {
                    "clock_out_time": datetime.utcnow().isoformat(),
                    "clock_out_location": {"lat": latitude, "lng": longitude},
                    "status": "completed",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Update cleaner's total jobs
        cleaner = await db.cleaners.find_one({"email": current_user.email})
        if cleaner:
            await db.cleaners.update_one(
                {"id": cleaner.get("id")},
                {"$inc": {"total_jobs": 1}}
            )
        
        # Get updated booking
        updated_booking = await db.bookings.find_one({"id": jobId})
        
        return {
            "message": "Clocked out successfully",
            "job": {
                "id": updated_booking.get("id"),
                "status": "completed",
                "clockOutTime": updated_booking.get("clock_out_time")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clock out failed: {str(e)}")

@api_router.post("/cleaner/update-eta")
async def update_eta(
    jobId: str,
    eta: str,
    current_user: User = Depends(get_current_user)
):
    """Update estimated time of arrival for a job"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        await db.bookings.update_one(
            {"id": jobId},
            {
                "$set": {
                    "eta": eta,
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        return {"message": "ETA updated successfully", "job": {"id": jobId, "eta": eta}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ETA: {str(e)}")

@api_router.post("/cleaner/send-message")
async def send_message_to_client(
    jobId: str,
    message: str,
    current_user: User = Depends(get_current_user)
):
    """Send a message to the client"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get booking and customer info
        booking = await db.bookings.find_one({"id": jobId})
        if not booking:
            raise HTTPException(status_code=404, detail="Job not found")
        
        customer = await db.users.find_one({"id": booking.get("customer_id")})
        
        # Store message in database
        message_doc = {
            "id": str(uuid.uuid4()),
            "job_id": jobId,
            "sender_id": current_user.id,
            "sender_type": "cleaner",
            "receiver_id": booking.get("customer_id"),
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "is_read": False
        }
        await db.messages.insert_one(message_doc)
        
        # Send email notification if customer exists
        if customer and customer.get("email"):
            try:
                await email_service.send_email(
                    to_email=customer.get("email"),
                    subject=f"Message from your cleaner - Job #{jobId[:8]}",
                    body=f"Your cleaner sent you a message:\n\n{message}\n\nJob Date: {booking.get('booking_date')}\nTime: {booking.get('time_slot')}"
                )
            except Exception as e:
                print(f"Failed to send email notification: {str(e)}")
        
        return {"message": "Message sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

# ============================================================================
# CLEANER CALENDAR ENDPOINTS
# ============================================================================

@api_router.get("/cleaner/calendar")
async def get_cleaner_calendar(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_cleaner_user)
):
    """Get cleaner's calendar events"""
    try:
        # Get cleaner info
        cleaner = await db.cleaners.find_one({"id": current_user.id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Get bookings for this cleaner in date range
        bookings = await db.bookings.find({
            "cleaner_id": current_user.id,
            "booking_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("booking_date", 1).to_list(1000)

        # Get calendar events
        events = []
        for booking in bookings:
            # Parse time slot to create start/end times
            time_slot = booking.get("time_slot", "09:00-12:00")
            time_parts = time_slot.split("-")
            start_time_str = f"{booking['booking_date']}T{time_parts[0]}:00"
            end_time_str = f"{booking['booking_date']}T{time_parts[1] if len(time_parts) > 1 else '12:00'}:00"

            event = {
                "id": booking["id"],
                "title": f"Cleaning - Customer {booking.get('customer_id', '')[:8]}",
                "start": start_time_str,
                "end": end_time_str,
                "type": "booking",
                "status": booking.get("status", "pending"),
                "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
                "address": booking.get("address", {}).get("street", ""),
                "amount": booking.get("total_amount", 0),
                "notes": booking.get("special_instructions", "")
            }
            events.append(event)

        return {
            "cleaner_id": current_user.id,
            "cleaner_name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
            "events": events,
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar: {str(e)}")

@api_router.get("/cleaner/calendar/events")
async def get_cleaner_calendar_events(
    current_user: User = Depends(get_cleaner_user)
):
    """Get cleaner's upcoming calendar events"""
    try:
        # Get cleaner info
        cleaner = await db.cleaners.find_one({"id": current_user.id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")

        # Get today's and next 7 days bookings
        today = datetime.now().strftime("%Y-%m-%d")
        next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        bookings = await db.bookings.find({
            "cleaner_id": current_user.id,
            "booking_date": {
                "$gte": today,
                "$lte": next_week
            }
        }).sort("booking_date", 1).to_list(1000)

        events = []
        for booking in bookings:
            # Parse time slot to create start/end times
            time_slot = booking.get("time_slot", "09:00-12:00")
            time_parts = time_slot.split("-")
            start_time_str = f"{booking['booking_date']}T{time_parts[0]}:00"
            end_time_str = f"{booking['booking_date']}T{time_parts[1] if len(time_parts) > 1 else '12:00'}:00"

            event = {
                "id": booking["id"],
                "title": f"Cleaning Job",
                "start": start_time_str,
                "end": end_time_str,
                "type": "booking",
                "status": booking.get("status", "pending"),
                "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
                "address": booking.get("address", {}).get("street", ""),
                "amount": booking.get("total_amount", 0),
                "notes": booking.get("special_instructions", "")
            }
            events.append(event)

        return {
            "cleaner_id": current_user.id,
            "events": events,
            "total_events": len(events)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar events: {str(e)}")

@api_router.get("/availability")
async def get_availability(
    date: str,
    time_slot: Optional[str] = None
):
    """Check availability for booking on a specific date"""
    try:
        # Get all active cleaners
        cleaners = await db.cleaners.find({"is_active": True}).to_list(1000)

        if not cleaners:
            return {
                "date": date,
                "available": False,
                "available_cleaners": 0,
                "total_cleaners": 0,
                "message": "No cleaners available"
            }

        # Check if any cleaner has calendar integration and is available
        available_cleaners = 0

        for cleaner in cleaners:
            if cleaner.get('calendar_integration_enabled') and cleaner.get('google_calendar_credentials'):
                # Check Google Calendar availability
                credentials = cleaner['google_calendar_credentials']
                service = calendar_service.create_service_from_credentials_dict(credentials)

                if service:
                    # Parse time slot or use default
                    slot = time_slot or "09:00-12:00"
                    start_time, end_time = slot.split('-')
                    job_date = datetime.fromisoformat(date)
                    start_datetime = datetime.combine(job_date.date(), datetime.strptime(start_time, "%H:%M").time())
                    end_datetime = datetime.combine(job_date.date(), datetime.strptime(end_time, "%H:%M").time())

                    is_available = calendar_service.check_availability(
                        service,
                        cleaner.get('google_calendar_id', 'primary'),
                        start_datetime,
                        end_datetime
                    )

                    if is_available:
                        available_cleaners += 1
            else:
                # For cleaners without working calendar integration, assume they are available for testing
                # In a real scenario, you might want to check their existing bookings
                available_cleaners += 1

        return {
            "date": date,
            "time_slot": time_slot,
            "available": available_cleaners > 0,
            "available_cleaners": available_cleaners,
            "total_cleaners": len(cleaners),
            "message": f"{available_cleaners} of {len(cleaners)} cleaners available"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check availability: {str(e)}")

@api_router.get("/cleaner/earnings")
async def get_cleaner_earnings(current_user: User = Depends(get_current_user)):
    """Get cleaner earnings information"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        cleaner = await db.cleaners.find_one({"email": current_user.email})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner profile not found")
        
        # Get completed jobs for this cleaner
        completed_bookings = await db.bookings.find({
            "cleaner_id": cleaner.get("id"),
            "status": "completed"
        }).to_list(1000)
        
        total_earnings = sum(booking.get("total_amount", 0) * 0.7 for booking in completed_bookings)  # Assuming 70% commission
        
        return {
            "earnings": {
                "id": str(uuid.uuid4()),
                "cleanerId": cleaner.get("id"),
                "balance": total_earnings,
                "totalEarnings": total_earnings,
                "totalWithdrawals": 0,
                "recentTransactions": []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get earnings: {str(e)}")

@api_router.get("/cleaner/wallet")
async def get_cleaner_wallet(current_user: User = Depends(get_current_user)):
    """Get cleaner wallet information"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        cleaner = await db.cleaners.find_one({"email": current_user.email})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner profile not found")
        
        # Get completed jobs
        completed_bookings = await db.bookings.find({
            "cleaner_id": cleaner.get("id"),
            "status": "completed"
        }).to_list(1000)
        
        total_earnings = sum(booking.get("total_amount", 0) * 0.7 for booking in completed_bookings)
        
        return {
            "wallet": {
                "id": str(uuid.uuid4()),
                "cleanerId": cleaner.get("id"),
                "balance": total_earnings,
                "totalEarnings": total_earnings,
                "totalWithdrawals": 0,
                "recentTransactions": []
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get wallet: {str(e)}")

@api_router.get("/cleaner/payments")
async def get_cleaner_payments(current_user: User = Depends(get_current_user)):
    """Get cleaner payment history"""
    if current_user.role != UserRole.CLEANER:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        cleaner = await db.cleaners.find_one({"email": current_user.email})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner profile not found")
        
        # Get completed jobs
        completed_bookings = await db.bookings.find({
            "cleaner_id": cleaner.get("id"),
            "status": "completed"
        }).sort("booking_date", -1).to_list(1000)
        
        payments = []
        for booking in completed_bookings:
            customer = await db.users.find_one({"id": booking.get("customer_id")})
            customer_name = "Guest Customer"
            if customer:
                customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
            
            payment = {
                "id": str(uuid.uuid4()),
                "jobId": booking.get("id"),
                "clientName": customer_name,
                "amount": booking.get("total_amount", 0) * 0.7,
                "status": "completed",
                "type": "earnings",
                "date": booking.get("updated_at", datetime.utcnow().isoformat()),
                "transactionId": f"TXN-{booking.get('id')[:8]}"
            }
            payments.append(payment)
        
        return {"payments": payments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payments: {str(e)}")

# ============================================================================
# END CLEANER API ENDPOINTS
# ============================================================================

# ============================================================================
# CUSTOM CALENDAR API ENDPOINTS
# ============================================================================

# Calendar availability for customers (booking)
@api_router.get("/calendar/available-dates")
async def get_available_dates(
    start_date: str,
    end_date: str
):
    """Get available dates for booking between start and end date"""
    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        available_dates = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Check if date has available time slots
            time_slots_cursor = db.time_slot_availability.find({
                "date": date_str,
                "is_available": True,
                "is_blocked": False
            })
            time_slots = await time_slots_cursor.to_list(100)
            
            # Get available time slots for this date
            available_time_slots = []
            for slot in time_slots:
                if slot.get("booked_count", 0) < slot.get("total_capacity", 5):
                    available_time_slots.append({
                        "time_slot": slot.get("time_slot"),
                        "available_spots": slot.get("total_capacity", 5) - slot.get("booked_count", 0),
                        "total_capacity": slot.get("total_capacity", 5)
                    })
            
            if available_time_slots:
                available_dates.append({
                    "date": date_str,
                    "day_name": current_date.strftime("%A"),
                    "is_available": True,
                    "time_slots": available_time_slots
                })
            
            current_date += timedelta(days=1)
        
        return {"available_dates": available_dates}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available dates: {str(e)}")

@api_router.get("/calendar/time-slots/{date}")
async def get_time_slots_for_date(date: str):
    """Get all time slots and their availability for a specific date"""
    try:
        # Get time slot availability
        slots_cursor = db.time_slot_availability.find({"date": date})
        slots = await slots_cursor.to_list(100)
        
        time_slots = []
        for slot in slots:
            time_slots.append({
                "id": slot.get("id"),
                "time_slot": slot.get("time_slot"),
                "is_available": slot.get("is_available", True) and not slot.get("is_blocked", False),
                "is_blocked": slot.get("is_blocked", False),
                "blocked_reason": slot.get("blocked_reason"),
                "total_capacity": slot.get("total_capacity", 5),
                "booked_count": slot.get("booked_count", 0),
                "available_spots": slot.get("total_capacity", 5) - slot.get("booked_count", 0)
            })
        
        return {"date": date, "time_slots": time_slots}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get time slots: {str(e)}")

# Admin Calendar Management
@api_router.get("/admin/calendar/overview")
async def get_calendar_overview(
    start_date: str,
    end_date: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get complete calendar overview for admin with all bookings and cleaner schedules"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get all bookings in date range
        bookings_cursor = db.bookings.find({
            "booking_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        bookings = await bookings_cursor.to_list(1000)
        
        # Get all calendar events in date range
        events_cursor = db.calendar_events.find({
            "start_time": {
                "$gte": start.isoformat(),
                "$lte": end.isoformat()
            }
        })
        events = await events_cursor.to_list(1000)
        
        # Get all cleaners
        cleaners_cursor = db.cleaners.find({"is_active": True})
        cleaners = await cleaners_cursor.to_list(100)
        
        # Organize data by date
        calendar_data = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Get bookings for this date
            date_bookings = [b for b in bookings if b.get("booking_date") == date_str]
            
            # Get events for this date
            date_events = [e for e in events if e.get("start_time", "").startswith(date_str)]
            
            # Get cleaner availability
            cleaner_schedules = []
            for cleaner in cleaners:
                cleaner_id = cleaner.get("id")
                cleaner_bookings = [b for b in date_bookings if b.get("cleaner_id") == cleaner_id]
                cleaner_events = [e for e in date_events if e.get("cleaner_id") == cleaner_id]
                
                cleaner_schedules.append({
                    "cleaner_id": cleaner_id,
                    "cleaner_name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
                    "bookings_count": len(cleaner_bookings),
                    "events_count": len(cleaner_events),
                    "is_available": len(cleaner_bookings) < 3  # Max 3 jobs per day
                })
            
            calendar_data.append({
                "date": date_str,
                "day_name": current_date.strftime("%A"),
                "bookings_count": len(date_bookings),
                "events_count": len(date_events),
                "cleaner_schedules": cleaner_schedules,
                "bookings": date_bookings,
                "events": date_events
            })
            
            current_date += timedelta(days=1)
        
        return {"calendar_overview": calendar_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar overview: {str(e)}")

@api_router.post("/admin/calendar/block-date")
async def block_date(
    date: str,
    time_slot: Optional[str] = None,
    reason: str = "",
    admin_user: User = Depends(get_admin_user)
):
    """Block a date or specific time slot from bookings"""
    try:
        if time_slot:
            # Block specific time slot
            result = await db.time_slot_availability.update_one(
                {"date": date, "time_slot": time_slot},
                {
                    "$set": {
                        "is_blocked": True,
                        "blocked_reason": reason,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                },
                upsert=True
            )
        else:
            # Block entire date (all time slots)
            await db.time_slot_availability.update_many(
                {"date": date},
                {
                    "$set": {
                        "is_blocked": True,
                        "blocked_reason": reason,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        
        return {"message": "Date/time slot blocked successfully", "date": date, "time_slot": time_slot}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to block date: {str(e)}")

@api_router.post("/admin/calendar/unblock-date")
async def unblock_date(
    date: str,
    time_slot: Optional[str] = None,
    admin_user: User = Depends(get_admin_user)
):
    """Unblock a date or specific time slot"""
    try:
        if time_slot:
            # Unblock specific time slot
            await db.time_slot_availability.update_one(
                {"date": date, "time_slot": time_slot},
                {
                    "$set": {
                        "is_blocked": False,
                        "blocked_reason": None,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        else:
            # Unblock entire date
            await db.time_slot_availability.update_many(
                {"date": date},
                {
                    "$set": {
                        "is_blocked": False,
                        "blocked_reason": None,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
        
        return {"message": "Date/time slot unblocked successfully", "date": date, "time_slot": time_slot}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unblock date: {str(e)}")

# Cleaner availability management
@api_router.get("/admin/calendar/cleaner-availability/{cleaner_id}")
async def get_cleaner_availability(
    cleaner_id: str,
    start_date: str,
    end_date: str,
    admin_user: User = Depends(get_admin_user)
):
    """Get cleaner's availability and schedule for a date range"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Get cleaner info
        cleaner = await db.cleaners.find_one({"id": cleaner_id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")
        
        # Get bookings for this cleaner
        bookings_cursor = db.bookings.find({
            "cleaner_id": cleaner_id,
            "booking_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        })
        bookings = await bookings_cursor.to_list(1000)
        
        # Get calendar events
        events_cursor = db.calendar_events.find({
            "cleaner_id": cleaner_id,
            "start_time": {
                "$gte": start.isoformat(),
                "$lte": end.isoformat()
            }
        })
        events = await events_cursor.to_list(1000)
        
        # Organize by date
        availability_data = []
        current_date = start
        
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            date_bookings = [b for b in bookings if b.get("booking_date") == date_str]
            date_events = [e for e in events if e.get("start_time", "").startswith(date_str)]
            
            availability_data.append({
                "date": date_str,
                "day_name": current_date.strftime("%A"),
                "is_available": len(date_bookings) < 3,  # Max 3 jobs per day
                "bookings": date_bookings,
                "events": date_events,
                "bookings_count": len(date_bookings),
                "capacity_remaining": max(0, 3 - len(date_bookings))
            })
            
            current_date += timedelta(days=1)
        
        return {
            "cleaner": {
                "id": cleaner.get("id"),
                "name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
                "email": cleaner.get("email"),
                "rating": cleaner.get("rating", 5.0)
            },
            "availability": availability_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaner availability: {str(e)}")

@api_router.post("/admin/calendar/assign-to-cleaner")
async def assign_booking_to_cleaner(
    booking_id: str,
    cleaner_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Assign a booking to a cleaner and update calendar"""
    try:
        # Get booking
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Get cleaner
        cleaner = await db.cleaners.find_one({"id": cleaner_id})
        if not cleaner:
            raise HTTPException(status_code=404, detail="Cleaner not found")
        
        # Check cleaner availability for that date
        booking_date = booking.get("booking_date")
        existing_bookings = await db.bookings.count_documents({
            "cleaner_id": cleaner_id,
            "booking_date": booking_date,
            "status": {"$in": ["confirmed", "in_progress"]}
        })
        
        if existing_bookings >= 3:
            raise HTTPException(status_code=409, detail="Cleaner is fully booked for this date")
        
        # Update booking with cleaner assignment
        await db.bookings.update_one(
            {"id": booking_id},
            {
                "$set": {
                    "cleaner_id": cleaner_id,
                    "status": "confirmed",
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Create calendar event
        time_slot = booking.get("time_slot", "09:00-12:00")
        time_parts = time_slot.split("-")
        start_time_str = f"{booking_date}T{time_parts[0]}:00"
        end_time_str = f"{booking_date}T{time_parts[1] if len(time_parts) > 1 else '12:00'}:00"
        
        customer = await db.users.find_one({"id": booking.get("customer_id")})
        customer_name = "Guest"
        if customer:
            customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}"
        
        calendar_event = CalendarEvent(
            title=f"Cleaning - {customer_name}",
            description=f"{booking.get('house_size', '')} - {booking.get('frequency', '')}",
            event_type="booking",
            start_time=datetime.fromisoformat(start_time_str),
            end_time=datetime.fromisoformat(end_time_str),
            cleaner_id=cleaner_id,
            booking_id=booking_id,
            customer_id=booking.get("customer_id"),
            status="scheduled",
            color="#4CAF50",
            notes=booking.get("special_instructions")
        )
        
        await db.calendar_events.insert_one(prepare_for_mongo(calendar_event.dict()))
        
        # Update time slot availability
        await db.time_slot_availability.update_one(
            {"date": booking_date, "time_slot": time_slot},
            {
                "$inc": {"booked_count": 1},
                "$set": {"updated_at": datetime.utcnow().isoformat()}
            },
            upsert=True
        )
        
        return {
            "message": "Booking assigned to cleaner successfully",
            "booking_id": booking_id,
            "cleaner_id": cleaner_id,
            "cleaner_name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}",
            "event_created": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign booking: {str(e)}")

@api_router.get("/admin/calendar/events")
async def get_calendar_events(
    start_date: str,
    end_date: str,
    cleaner_id: Optional[str] = None,
    admin_user: User = Depends(get_admin_user)
):
    """Get all calendar events for admin view"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        query = {
            "start_time": {
                "$gte": start.isoformat(),
                "$lte": end.isoformat()
            }
        }
        
        if cleaner_id:
            query["cleaner_id"] = cleaner_id
        
        events_cursor = db.calendar_events.find(query)
        events = await events_cursor.to_list(1000)
        
        formatted_events = []
        for event in events:
            formatted_events.append({
                "id": event.get("id"),
                "title": event.get("title"),
                "description": event.get("description"),
                "event_type": event.get("event_type"),
                "start": event.get("start_time"),
                "end": event.get("end_time"),
                "cleaner_id": event.get("cleaner_id"),
                "booking_id": event.get("booking_id"),
                "customer_id": event.get("customer_id"),
                "status": event.get("status"),
                "color": event.get("color", "#2196F3"),
                "notes": event.get("notes")
            })
        
        return {"events": formatted_events}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get calendar events: {str(e)}")

# Initialize time slot availability (helper function)
async def initialize_time_slot_availability(days_ahead: int = 90):
    """Initialize time slot availability for next N days"""
    time_slots = [
        "08:00-10:00",
        "10:00-12:00",
        "12:00-14:00",
        "14:00-16:00",
        "16:00-18:00"
    ]
    
    today = datetime.now()
    
    for day_offset in range(days_ahead):
        date = today + timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")
        
        for time_slot in time_slots:
            # Check if already exists
            existing = await db.time_slot_availability.find_one({
                "date": date_str,
                "time_slot": time_slot
            })
            
            if not existing:
                slot_data = TimeSlotAvailability(
                    date=date_str,
                    time_slot=time_slot,
                    total_capacity=5,  # 5 cleaners can work this slot
                    booked_count=0
                )
                await db.time_slot_availability.insert_one(prepare_for_mongo(slot_data.dict()))

# ============================================================================
# END CUSTOM CALENDAR API ENDPOINTS
# ============================================================================

# Initialize database with default data
async def initialize_database():
    """Initialize database with default services and time slots"""
    
    # Create admin user if it doesn't exist
    admin_user = await db.users.find_one({"email": "admin@maids.com"})
    if not admin_user:
        admin = User(
            email="admin@maids.com",
            first_name="Admin",
            last_name="User",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN
        )
        await db.users.insert_one(prepare_for_mongo(admin.dict()))
        print("Created admin user: admin@maids.com / admin123")
    
    # Create demo customer if it doesn't exist
    demo_customer = await db.users.find_one({"email": "test@maids.com"})
    if not demo_customer:
        customer = User(
            email="test@maids.com",
            first_name="Test",
            last_name="Customer",
            phone="(555) 123-4567",
            password_hash=hash_password("test@maids@1234"),
            role=UserRole.CUSTOMER
        )
        await db.users.insert_one(prepare_for_mongo(customer.dict()))
        print("Created demo customer: test@maids.com / test@maids@1234")
    
    # Create demo cleaner if it doesn't exist
    demo_cleaner_user = await db.users.find_one({"email": "cleaner@maids.com"})
    if not demo_cleaner_user:
        cleaner_user = User(
            email="cleaner@maids.com",
            first_name="Demo",
            last_name="Cleaner",
            phone="(555) 987-6543",
            password_hash=hash_password("cleaner123"),
            role=UserRole.CLEANER
        )
        await db.users.insert_one(prepare_for_mongo(cleaner_user.dict()))
        print("Created demo cleaner user: cleaner@maids.com / cleaner123")
    
    # Create demo cleaner profile if it doesn't exist
    demo_cleaner = await db.cleaners.find_one({"email": "cleaner@maids.com"})
    if not demo_cleaner:
        cleaner = Cleaner(
            email="cleaner@maids.com",
            first_name="Demo",
            last_name="Cleaner",
            phone="(555) 987-6543",
            rating=4.8,
            total_jobs=45
        )
        await db.cleaners.insert_one(prepare_for_mongo(cleaner.dict()))
        print("Created demo cleaner profile")
    
    # Create default services if they don't exist
    services_count = await db.services.count_documents({})
    if services_count == 0:
        default_services = [
            {"name": "Blinds (feather dusting)", "category": "a_la_carte", "description": "Feather dusting only", "a_la_carte_price": 10.00, "is_a_la_carte": True},
            {"name": "Inside Kitchen/Bathroom Cabinets (move-out only)", "category": "a_la_carte", "description": "Wiping out using micro fiber", "a_la_carte_price": 80.00, "is_a_la_carte": True},
            {"name": "Oven Cleaning", "category": "a_la_carte", "description": "Cleaning of 1 Oven. Double oven is double the cost", "a_la_carte_price": 40.00, "is_a_la_carte": True},
            {"name": "Dust Baseboards ≤ 2500 sq ft", "category": "a_la_carte", "description": "Feather dust under 2500 sq ft", "a_la_carte_price": 20.00, "is_a_la_carte": True},
            {"name": "Dust Baseboards > 2500 sq ft", "category": "a_la_carte", "description": "Feather dust over 2500 sq ft", "a_la_carte_price": 30.00, "is_a_la_carte": True},
            {"name": "Dust Shutters ≤ 2500 sq ft", "category": "a_la_carte", "description": "Feather dust under 2500 sq ft", "a_la_carte_price": 40.00, "is_a_la_carte": True},
            {"name": "Dust Shutters > 2500 sq ft", "category": "a_la_carte", "description": "Feather dust over 2500 sq ft", "a_la_carte_price": 60.00, "is_a_la_carte": True},
            {"name": "Hand-clean Baseboards ≤ 2500 sq ft", "category": "a_la_carte", "description": "Hand wipe under 2500 sq ft", "a_la_carte_price": 60.00, "is_a_la_carte": True},
            {"name": "Hand-clean Baseboards > 2500 sq ft", "category": "a_la_carte", "description": "Hand wipe over 2500 sq ft", "a_la_carte_price": 80.00, "is_a_la_carte": True},
            {"name": "Inside Refrigerator", "category": "a_la_carte", "description": "Clean inside of Fridge (not Freezer)", "a_la_carte_price": 45.00, "is_a_la_carte": True},
            {"name": "Vacuum Couch", "category": "a_la_carte", "description": "Top and Underneath (Includes 1 couch and 1 love seat combo or 1 sectional)", "a_la_carte_price": 15.00, "is_a_la_carte": True},
            {"name": "Clean Exterior Kitchen/Bathroom Cabinets", "category": "a_la_carte", "description": "Hand wipe all exterior upper and lower cabinets", "a_la_carte_price": 40.00, "is_a_la_carte": True}
        ]
        
        for service_data in default_services:
            service = Service(**service_data)
            await db.services.insert_one(prepare_for_mongo(service.dict()))
        
        print("Created default services")
    
    # Create time slots for next 30 days if they don't exist
    slots_count = await db.time_slots.count_documents({})
    if slots_count == 0:
        time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00", "16:00-18:00"]
        
        for i in range(30):  # Next 30 days
            slot_date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            
            for time_slot in time_slots:
                slot = TimeSlot(date=slot_date, time_slot=time_slot)
                await db.time_slots.insert_one(prepare_for_mongo(slot.dict()))
        
        print("Created time slots for next 30 days")
    
    # Initialize custom calendar time slot availability
    availability_count = await db.time_slot_availability.count_documents({})
    if availability_count == 0:
        await initialize_time_slot_availability(90)  # Initialize for next 90 days
        print("Initialized calendar time slot availability for next 90 days")

# Startup event moved to lifespan handler

# Reports endpoints
@api_router.get("/admin/reports/weekly")
async def get_weekly_report(admin_user: User = Depends(get_admin_user)):
    """Get weekly report data"""
    from datetime import datetime, timedelta
    
    # Get current week start and end
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get bookings for this week
    bookings = await db.bookings.find({
        "booking_date": {
            "$gte": week_start.strftime("%Y-%m-%d"),
            "$lte": week_end.strftime("%Y-%m-%d")
        }
    }).to_list(1000)
    
    # Calculate stats
    total_bookings = len(bookings)
    revenue = sum(booking.get("total_amount", 0) for booking in bookings)
    cancellations = len([b for b in bookings if b.get("status") == "cancelled"])
    reschedules = len([b for b in bookings if b.get("status") == "rescheduled"])
    completed = len([b for b in bookings if b.get("status") == "completed"])
    
    completion_rate = (completed / total_bookings * 100) if total_bookings > 0 else 0
    avg_booking_value = (revenue / total_bookings) if total_bookings > 0 else 0
    
    # Get cleaner job completion data
    cleaner_completions = []
    for booking in bookings:
        if booking.get("status") == "completed" and booking.get("cleaner_id"):
            cleaner = await db.cleaners.find_one({"id": booking["cleaner_id"]})
            if cleaner:
                cleaner_completions.append({
                    "cleaner_id": booking["cleaner_id"],
                    "cleaner_name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}".strip(),
                    "job_id": booking["id"],
                    "completed_at": booking.get("completed_at"),
                    "completion_notes": booking.get("completion_notes", ""),
                    "total_amount": booking.get("total_amount", 0)
                })
    
    # Group completions by cleaner
    cleaner_stats = {}
    for completion in cleaner_completions:
        cleaner_id = completion["cleaner_id"]
        if cleaner_id not in cleaner_stats:
            cleaner_stats[cleaner_id] = {
                "cleaner_name": completion["cleaner_name"],
                "jobs_completed": 0,
                "total_revenue": 0,
                "completions": []
            }
        cleaner_stats[cleaner_id]["jobs_completed"] += 1
        cleaner_stats[cleaner_id]["total_revenue"] += completion["total_amount"]
        cleaner_stats[cleaner_id]["completions"].append(completion)
    
    return {
        "totalBookings": total_bookings,
        "revenue": round(revenue, 2),
        "cancellations": cancellations,
        "reschedules": reschedules,
        "completionRate": round(completion_rate, 1),
        "customerSatisfaction": 95.0,  # Placeholder - would come from feedback system
        "avgBookingValue": round(avg_booking_value, 2),
        "cleanerCompletions": list(cleaner_stats.values()),
        "totalCleanerCompletions": len(cleaner_completions)
    }

@api_router.get("/admin/reports/monthly")
async def get_monthly_report(admin_user: User = Depends(get_admin_user)):
    """Get monthly report data"""
    from datetime import datetime, timedelta
    
    # Get current month start and end
    today = datetime.now()
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Get bookings for this month
    bookings = await db.bookings.find({
        "booking_date": {
            "$gte": month_start.strftime("%Y-%m-%d"),
            "$lte": month_end.strftime("%Y-%m-%d")
        }
    }).to_list(1000)
    
    # Calculate stats
    total_bookings = len(bookings)
    revenue = sum(booking.get("total_amount", 0) for booking in bookings)
    cancellations = len([b for b in bookings if b.get("status") == "cancelled"])
    reschedules = len([b for b in bookings if b.get("status") == "rescheduled"])
    completed = len([b for b in bookings if b.get("status") == "completed"])
    
    completion_rate = (completed / total_bookings * 100) if total_bookings > 0 else 0
    avg_booking_value = (revenue / total_bookings) if total_bookings > 0 else 0
    
    # Get cleaner job completion data
    cleaner_completions = []
    for booking in bookings:
        if booking.get("status") == "completed" and booking.get("cleaner_id"):
            cleaner = await db.cleaners.find_one({"id": booking["cleaner_id"]})
            if cleaner:
                cleaner_completions.append({
                    "cleaner_id": booking["cleaner_id"],
                    "cleaner_name": f"{cleaner.get('first_name', '')} {cleaner.get('last_name', '')}".strip(),
                    "job_id": booking["id"],
                    "completed_at": booking.get("completed_at"),
                    "completion_notes": booking.get("completion_notes", ""),
                    "total_amount": booking.get("total_amount", 0)
                })
    
    # Group completions by cleaner
    cleaner_stats = {}
    for completion in cleaner_completions:
        cleaner_id = completion["cleaner_id"]
        if cleaner_id not in cleaner_stats:
            cleaner_stats[cleaner_id] = {
                "cleaner_name": completion["cleaner_name"],
                "jobs_completed": 0,
                "total_revenue": 0,
                "completions": []
            }
        cleaner_stats[cleaner_id]["jobs_completed"] += 1
        cleaner_stats[cleaner_id]["total_revenue"] += completion["total_amount"]
        cleaner_stats[cleaner_id]["completions"].append(completion)
    
    return {
        "totalBookings": total_bookings,
        "revenue": round(revenue, 2),
        "cancellations": cancellations,
        "reschedules": reschedules,
        "completionRate": round(completion_rate, 1),
        "customerSatisfaction": 95.0,  # Placeholder - would come from feedback system
        "avgBookingValue": round(avg_booking_value, 2),
        "cleanerCompletions": list(cleaner_stats.values()),
        "totalCleanerCompletions": len(cleaner_completions)
    }

@api_router.get("/admin/reports/{report_type}/export")
async def export_report(report_type: str, admin_user: User = Depends(get_admin_user)):
    """Export report data as CSV"""
    from datetime import datetime, timedelta
    
    if report_type == "weekly":
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        bookings = await db.bookings.find({
            "booking_date": {
                "$gte": week_start.strftime("%Y-%m-%d"),
                "$lte": week_end.strftime("%Y-%m-%d")
            }
        }).to_list(1000)
    else:  # monthly
        today = datetime.now()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        bookings = await db.bookings.find({
            "booking_date": {
                "$gte": month_start.strftime("%Y-%m-%d"),
                "$lte": month_end.strftime("%Y-%m-%d")
            }
        }).to_list(1000)
    
    # Format data for CSV export
    export_data = []
    for booking in bookings:
        export_data.append({
            "booking_id": booking.get("id", ""),
            "customer_id": booking.get("customer_id", ""),
            "booking_date": booking.get("booking_date", ""),
            "time_slot": booking.get("time_slot", ""),
            "house_size": booking.get("house_size", ""),
            "frequency": booking.get("frequency", ""),
            "total_amount": booking.get("total_amount", 0),
            "status": booking.get("status", ""),
            "cleaner_id": booking.get("cleaner_id", ""),
            "created_at": booking.get("created_at", "")
        })
    
    return {"data": export_data}

# Order Management endpoints
@api_router.get("/admin/orders/pending")
async def get_pending_orders(admin_user: User = Depends(get_admin_user)):
    """Get pending cancellations and reschedules"""
    # Get bookings with pending status changes
    pending_bookings = await db.bookings.find({
        "status": {"$in": ["pending_cancellation", "pending_reschedule"]}
    }).to_list(1000)
    
    cancellations = []
    reschedules = []
    
    for booking in pending_bookings:
        if booking.get("status") == "pending_cancellation":
            cancellations.append({
                "id": booking.get("id"),
                "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
                "booking_date": booking.get("booking_date"),
                "total_amount": booking.get("total_amount")
            })
        elif booking.get("status") == "pending_reschedule":
            reschedules.append({
                "id": booking.get("id"),
                "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
                "original_date": booking.get("booking_date"),
                "new_date": booking.get("new_booking_date", booking.get("booking_date")),
                "total_amount": booking.get("total_amount")
            })
    
    return {
        "cancellations": cancellations,
        "reschedules": reschedules
    }

@api_router.get("/admin/orders/history")
async def get_order_history(admin_user: User = Depends(get_admin_user)):
    """Get order change history"""
    # Get recent bookings with status changes
    recent_bookings = await db.bookings.find({
        "status": {"$in": ["cancelled", "rescheduled"]},
        "updated_at": {"$gte": (datetime.now() - timedelta(days=30)).isoformat()}
    }).sort("updated_at", -1).limit(50).to_list(50)
    
    history = []
    for booking in recent_bookings:
        history.append({
            "id": booking.get("id"),
            "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
            "type": "cancellation" if booking.get("status") == "cancelled" else "reschedule",
            "timestamp": booking.get("updated_at", booking.get("created_at"))
        })
    
    return history

@api_router.post("/admin/orders/{order_id}/approve_cancellation")
async def approve_cancellation(order_id: str, admin_user: User = Depends(get_admin_user)):
    """Approve a cancellation request"""
    result = await db.bookings.update_one(
        {"id": order_id, "status": "pending_cancellation"},
        {"$set": {"status": "cancelled", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pending cancellation not found")
    
    return {"message": "Cancellation approved"}

@api_router.post("/admin/orders/{order_id}/deny_cancellation")
async def deny_cancellation(order_id: str, admin_user: User = Depends(get_admin_user)):
    """Deny a cancellation request"""
    result = await db.bookings.update_one(
        {"id": order_id, "status": "pending_cancellation"},
        {"$set": {"status": "confirmed", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pending cancellation not found")
    
    return {"message": "Cancellation denied"}

@api_router.post("/admin/orders/{order_id}/approve_reschedule")
async def approve_reschedule(order_id: str, admin_user: User = Depends(get_admin_user)):
    """Approve a reschedule request"""
    result = await db.bookings.update_one(
        {"id": order_id, "status": "pending_reschedule"},
        {"$set": {"status": "confirmed", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pending reschedule not found")
    
    return {"message": "Reschedule approved"}

@api_router.post("/admin/orders/{order_id}/deny_reschedule")
async def deny_reschedule(order_id: str, admin_user: User = Depends(get_admin_user)):
    """Deny a reschedule request"""
    result = await db.bookings.update_one(
        {"id": order_id, "status": "pending_reschedule"},
        {"$set": {"status": "confirmed", "updated_at": datetime.utcnow().isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pending reschedule not found")
    
    return {"message": "Reschedule denied"}

# Stripe Payment Endpoints
@api_router.get("/stripe/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return {"publishable_key": STRIPE_PUBLISHABLE_KEY}

@api_router.post("/payment-methods", response_model=PaymentMethod)
async def create_payment_method_endpoint(
    payment_data: PaymentMethodCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new payment method for the user"""
    
    # Rate limiting check
    if not rate_limit_check(current_user.id, "create_payment_method"):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Sanitize inputs
    payment_data.cardholder_name = sanitize_input(payment_data.cardholder_name)
    
    # Validate card data
    if not validate_card_number(payment_data.card_number):
        raise HTTPException(status_code=400, detail="Invalid card number")
    
    if not validate_cvc(payment_data.cvc):
        raise HTTPException(status_code=400, detail="Invalid CVC")
    
    if not validate_expiry_date(payment_data.expiry_month, payment_data.expiry_year):
        raise HTTPException(status_code=400, detail="Invalid expiry date")
    
    # Validate cardholder name
    if not payment_data.cardholder_name or len(payment_data.cardholder_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Cardholder name must be at least 2 characters")
    
    # Check for duplicate payment methods
    existing_methods = await db.payment_methods.find({
        "customer_id": current_user.id,
        "last_four": payment_data.card_number[-4:]
    }).to_list(length=None)
    
    if existing_methods:
        raise HTTPException(status_code=400, detail="Payment method with this card already exists")
    
    try:
        # Get or create Stripe customer
        user = await db.users.find_one({"id": current_user.id})
        stripe_customer_id = user.get('stripe_customer_id')
        
        if not stripe_customer_id:
            stripe_customer_id = await create_stripe_customer(
                current_user.id, 
                current_user.email, 
                f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            )
            # Update user with Stripe customer ID
            await db.users.update_one(
                {"id": current_user.id},
                {"$set": {"stripe_customer_id": stripe_customer_id}}
            )
        
        # Create payment method in Stripe
        stripe_payment_method_id = await create_payment_method(
            stripe_customer_id,
            payment_data.dict()
        )
        
        # Get payment method details from Stripe
        payment_method = stripe.PaymentMethod.retrieve(stripe_payment_method_id)
        card = payment_method.card
        
        # If this is set as primary, unset other primary methods
        if payment_data.is_primary:
            await db.payment_methods.update_many(
                {"customer_id": current_user.id, "is_primary": True},
                {"$set": {"is_primary": False}}
            )
        
        # Create payment method record
        payment_method_record = PaymentMethod(
            customer_id=current_user.id,
            stripe_payment_method_id=stripe_payment_method_id,
            card_brand=card.brand,
            last_four=card.last4,
            expiry_month=card.exp_month,
            expiry_year=card.exp_year,
            is_primary=payment_data.is_primary
        )
        
        payment_method_dict = prepare_for_mongo(payment_method_record.dict())
        await db.payment_methods.insert_one(payment_method_dict)
        
        return payment_method_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment method: {str(e)}")

@api_router.get("/payment-methods", response_model=List[PaymentMethod])
async def get_payment_methods(current_user: User = Depends(get_current_user)):
    """Get user's payment methods"""
    try:
        payment_methods = await db.payment_methods.find({"customer_id": current_user.id}).to_list(length=None)
        return [PaymentMethod(**pm) for pm in payment_methods]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve payment methods: {str(e)}")

@api_router.put("/payment-methods/{payment_method_id}/set-primary")
async def set_primary_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Set a payment method as primary"""
    try:
        # Unset all primary methods for this user
        await db.payment_methods.update_many(
            {"customer_id": current_user.id, "is_primary": True},
            {"$set": {"is_primary": False}}
        )
        
        # Set the specified method as primary
        result = await db.payment_methods.update_one(
            {"id": payment_method_id, "customer_id": current_user.id},
            {"$set": {"is_primary": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        return {"message": "Primary payment method updated"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update primary payment method: {str(e)}")

@api_router.delete("/payment-methods/{payment_method_id}")
async def delete_payment_method(
    payment_method_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a payment method"""
    try:
        # Check if this is the only payment method
        payment_method_count = await db.payment_methods.count_documents({"customer_id": current_user.id})
        if payment_method_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot delete the last payment method")
        
        # Get payment method details
        payment_method = await db.payment_methods.find_one({
            "id": payment_method_id,
            "customer_id": current_user.id
        })
        
        if not payment_method:
            raise HTTPException(status_code=404, detail="Payment method not found")
        
        # Delete from Stripe
        try:
            stripe.PaymentMethod.detach(payment_method['stripe_payment_method_id'])
        except StripeError:
            pass  # Continue even if Stripe deletion fails
        
        # Delete from database
        await db.payment_methods.delete_one({"id": payment_method_id})
        
        return {"message": "Payment method deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment method: {str(e)}")

@api_router.post("/payment-intents", response_model=PaymentIntent)
async def create_payment_intent_endpoint(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a payment intent for a booking"""
    try:
        # Rate limiting check
        if not rate_limit_check(current_user.id, "create_payment_intent"):
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        
        # Validate payment amount
        if not validate_payment_amount(payment_data.amount / 100):  # Convert from cents
            raise HTTPException(status_code=400, detail="Invalid payment amount")
        
        # Get booking details
        booking = await db.bookings.find_one({"id": payment_data.booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Verify booking belongs to user
        if booking.get('customer_id') != current_user.id:
            raise HTTPException(status_code=403, detail="Booking does not belong to user")
        
        # Check if booking already has a payment intent
        existing_intent = await db.payment_intents.find_one({
            "booking_id": payment_data.booking_id,
            "customer_id": current_user.id
        })
        
        if existing_intent:
            raise HTTPException(status_code=400, detail="Payment intent already exists for this booking")
        
        # Verify payment amount matches booking total
        booking_total_cents = int(booking.get('total_amount', 0) * 100)
        if payment_data.amount != booking_total_cents:
            raise HTTPException(status_code=400, detail="Payment amount does not match booking total")
        
        # Get user's Stripe customer ID
        user = await db.users.find_one({"id": current_user.id})
        stripe_customer_id = user.get('stripe_customer_id')
        
        if not stripe_customer_id:
            raise HTTPException(status_code=400, detail="No Stripe customer found. Please add a payment method first.")
        
        # Create payment intent in Stripe
        payment_intent = await create_payment_intent(
            payment_data.amount,
            stripe_customer_id,
            payment_data.payment_method_id
        )
        
        # Create payment intent record
        payment_intent_record = PaymentIntent(
            booking_id=payment_data.booking_id,
            customer_id=current_user.id,
            stripe_payment_intent_id=payment_intent['id'],
            amount=payment_data.amount,
            currency=payment_data.currency,
            status=payment_intent['status'],
            payment_method_id=payment_data.payment_method_id
        )
        
        payment_intent_dict = prepare_for_mongo(payment_intent_record.dict())
        await db.payment_intents.insert_one(payment_intent_dict)
        
        return payment_intent_record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment intent: {str(e)}")

@api_router.post("/payment-intents/{payment_intent_id}/confirm")
async def confirm_payment_intent_endpoint(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Confirm a payment intent"""
    try:
        # Get payment intent from database
        payment_intent = await db.payment_intents.find_one({
            "id": payment_intent_id,
            "customer_id": current_user.id
        })
        
        if not payment_intent:
            raise HTTPException(status_code=404, detail="Payment intent not found")
        
        # Confirm payment in Stripe
        confirmed_intent = await confirm_payment_intent(payment_intent['stripe_payment_intent_id'])
        
        # Update payment intent status
        await db.payment_intents.update_one(
            {"id": payment_intent_id},
            {"$set": {"status": confirmed_intent['status'], "updated_at": datetime.utcnow().isoformat()}}
        )
        
        # Update booking payment status if payment succeeded
        if confirmed_intent['status'] == 'succeeded':
            await db.bookings.update_one(
                {"id": payment_intent['booking_id']},
                {"$set": {"payment_status": "paid", "updated_at": datetime.utcnow().isoformat()}}
            )
        
        return {"status": confirmed_intent['status'], "payment_intent": confirmed_intent}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm payment: {str(e)}")

@api_router.get("/payment-intents/{payment_intent_id}")
async def get_payment_intent_endpoint(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment intent status"""
    try:
        # Get payment intent from database
        payment_intent = await db.payment_intents.find_one({
            "id": payment_intent_id,
            "customer_id": current_user.id
        })
        
        if not payment_intent:
            raise HTTPException(status_code=404, detail="Payment intent not found")
        
        # Get latest status from Stripe
        stripe_intent = await get_payment_intent(payment_intent['stripe_payment_intent_id'])
        
        # Update local status if different
        if stripe_intent['status'] != payment_intent['status']:
            await db.payment_intents.update_one(
                {"id": payment_intent_id},
                {"$set": {"status": stripe_intent['status'], "updated_at": datetime.utcnow().isoformat()}}
            )
            payment_intent['status'] = stripe_intent['status']
        
        return payment_intent
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment intent: {str(e)}")

@api_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        if not STRIPE_WEBHOOK_SECRET:
            raise HTTPException(status_code=400, detail="Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Update booking payment status
            await db.bookings.update_many(
                {"payment_intent_id": payment_intent['id']},
                {"$set": {"payment_status": "paid", "updated_at": datetime.utcnow().isoformat()}}
            )
            
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            
            # Update booking payment status
            await db.bookings.update_many(
                {"payment_intent_id": payment_intent['id']},
                {"$set": {"payment_status": "failed", "updated_at": datetime.utcnow().isoformat()}}
            )
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook error: {str(e)}")

# Email Reminder Endpoints
@api_router.post("/admin/email-reminders/send-single")
async def send_single_email_reminder(
    booking_id: str,
    reminder_type: str = "upcoming",
    admin_user: User = Depends(get_admin_user)
):
    """Send a single email reminder for a specific booking"""
    try:
        # Get booking data
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Send email reminder
        success = email_service.send_booking_reminder(booking, reminder_type)
        
        if success:
            return {"message": "Email reminder sent successfully", "booking_id": booking_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email reminder")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email reminder: {str(e)}")

@api_router.post("/admin/email-reminders/send-batch")
async def send_batch_email_reminders(
    booking_ids: List[str],
    reminder_type: str = "upcoming",
    admin_user: User = Depends(get_admin_user)
):
    """Send email reminders for multiple bookings"""
    try:
        # Get booking data for all specified bookings
        bookings = await db.bookings.find({"id": {"$in": booking_ids}}).to_list(1000)
        
        if not bookings:
            raise HTTPException(status_code=404, detail="No bookings found")
        
        # Prepare email data
        email_list = []
        for booking in bookings:
            customer_email = None
            if booking.get('customer'):
                customer_email = booking['customer'].get('email')
            elif booking.get('user_id'):
                # Try to get email from user data
                user = await db.users.find_one({"id": booking['user_id']})
                if user:
                    customer_email = user.get('email')
            
            if customer_email:
                email_template = email_service.create_reminder_template(booking, reminder_type)
                email_list.append({
                    'to_email': customer_email,
                    'subject': email_template['subject'],
                    'html_content': email_template['html_content'],
                    'text_content': email_template['text_content']
                })
        
        # Send bulk emails
        results = email_service.send_bulk_emails(email_list)
        
        return {
            "message": "Batch email reminders processed",
            "total_bookings": len(bookings),
            "emails_sent": results['success'],
            "emails_failed": results['failed'],
            "errors": results['errors']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending batch email reminders: {str(e)}")

@api_router.get("/admin/email-reminders/upcoming")
async def get_upcoming_bookings_for_reminders(
    days_ahead: int = 7,
    admin_user: User = Depends(get_admin_user)
):
    """Get bookings that are coming up for sending reminders"""
    try:
        # Calculate date range
        today = datetime.now().date()
        future_date = today + timedelta(days=days_ahead)
        
        # Get upcoming bookings
        bookings = await db.bookings.find({
            "booking_date": {
                "$gte": today.strftime("%Y-%m-%d"),
                "$lte": future_date.strftime("%Y-%m-%d")
            },
            "status": {"$in": ["confirmed", "pending"]}
        }).sort("booking_date", 1).to_list(1000)
        
        # Format booking data for frontend
        formatted_bookings = []
        for booking in bookings:
            customer_email = None
            customer_name = "Unknown Customer"
            
            if booking.get('customer'):
                customer_email = booking['customer'].get('email')
                customer_name = f"{booking['customer'].get('first_name', '')} {booking['customer'].get('last_name', '')}".strip()
            elif booking.get('user_id'):
                user = await db.users.find_one({"id": booking['user_id']})
                if user:
                    customer_email = user.get('email')
                    customer_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            
            formatted_bookings.append({
                "id": booking['id'],
                "customer_name": customer_name,
                "customer_email": customer_email,
                "booking_date": booking['booking_date'],
                "time_slot": booking['time_slot'],
                "total_amount": booking.get('total_amount', 0),
                "status": booking['status'],
                "has_email": customer_email is not None
            })
        
        return {
            "bookings": formatted_bookings,
            "total_count": len(formatted_bookings),
            "date_range": {
                "from": today.strftime("%Y-%m-%d"),
                "to": future_date.strftime("%Y-%m-%d")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting upcoming bookings: {str(e)}")

@api_router.post("/admin/email-reminders/automated")
async def setup_automated_reminders(
    reminder_settings: Dict[str, Any],
    admin_user: User = Depends(get_admin_user)
):
    """Set up automated email reminders (for future implementation)"""
    try:
        # This would typically store reminder settings in the database
        # For now, we'll just return a success message
        return {
            "message": "Automated reminders configured",
            "settings": reminder_settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting up automated reminders: {str(e)}")

# Import reminder service
from services.reminder_service import ReminderService, ReminderTemplate, ReminderLog
from services.twilio_sms_service import sms_service
from services.reminder_scheduler import ReminderScheduler

# Initialize reminder service
reminder_service = ReminderService(db)
reminder_scheduler = ReminderScheduler(db, reminder_service)

# Reminder Templates Endpoints
@api_router.get("/reminder-templates")
async def get_reminder_templates(active_only: bool = True):
    """Get all reminder templates"""
    try:
        templates = await reminder_service.get_templates(active_only=active_only)
        return {"success": True, "templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@api_router.get("/reminder-templates/{template_id}")
async def get_reminder_template(template_id: str):
    """Get a specific reminder template"""
    try:
        template = await reminder_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return {"success": True, "template": template}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching template: {str(e)}")

@api_router.post("/reminder-templates")
async def create_reminder_template(template_data: dict, current_user: User = Depends(get_current_user)):
    """Create a new reminder template (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await reminder_service.create_template(template_data)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@api_router.put("/reminder-templates/{template_id}")
async def update_reminder_template(template_id: str, update_data: dict, current_user: User = Depends(get_current_user)):
    """Update a reminder template (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await reminder_service.update_template(template_id, update_data)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating template: {str(e)}")

@api_router.delete("/reminder-templates/{template_id}")
async def delete_reminder_template(template_id: str, current_user: User = Depends(get_current_user)):
    """Delete a reminder template (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        result = await reminder_service.delete_template(template_id)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting template: {str(e)}")

# Reminder Sending Endpoints
@api_router.post("/reminders/send")
async def send_reminder(booking_id: str, template_id: str, custom_message: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Send a reminder for a specific booking"""
    try:
        result = await reminder_service.send_reminder(booking_id, template_id, custom_message)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending reminder: {str(e)}")

@api_router.get("/reminders/logs")
async def get_reminder_logs(booking_id: Optional[str] = None, limit: int = 50, current_user: User = Depends(get_current_user)):
    """Get reminder logs"""
    try:
        logs = await reminder_service.get_reminder_logs(booking_id, limit)
        return {"success": True, "logs": logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reminder logs: {str(e)}")

@api_router.get("/reminders/sms-status")
async def get_sms_status():
    """Check if SMS service is configured and working"""
    try:
        is_configured = sms_service.is_configured()
        return {
            "success": True,
            "sms_configured": is_configured,
            "message": "SMS service is configured and ready" if is_configured else "SMS service is not configured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking SMS status: {str(e)}")

# Scheduler Management Endpoints
@api_router.post("/reminders/scheduler/start")
async def start_reminder_scheduler(current_user: User = Depends(get_current_user)):
    """Start the automatic reminder scheduler (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        await reminder_scheduler.start_scheduler()
        return {"success": True, "message": "Reminder scheduler started"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")

@api_router.post("/reminders/scheduler/stop")
async def stop_reminder_scheduler(current_user: User = Depends(get_current_user)):
    """Stop the automatic reminder scheduler (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        await reminder_scheduler.stop_scheduler()
        return {"success": True, "message": "Reminder scheduler stopped"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")

@api_router.get("/reminders/scheduler/status")
async def get_scheduler_status(current_user: User = Depends(get_current_user)):
    """Get the current status of the reminder scheduler"""
    try:
        status = await reminder_scheduler.get_scheduler_status()
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")

@api_router.post("/reminders/send-immediate")
async def send_immediate_reminder(booking_id: str, reminder_type: str, custom_message: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Send an immediate reminder for a specific booking"""
    try:
        from services.reminder_service import ReminderType
        
        # Validate reminder type
        try:
            reminder_type_enum = ReminderType(reminder_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid reminder type: {reminder_type}")
        
        result = await reminder_scheduler.send_immediate_reminder(booking_id, reminder_type_enum, custom_message)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending immediate reminder: {str(e)}")

# Reminder service initialization moved to lifespan handler

# Include the API router in the main app (already has /api prefix)
app.include_router(api_router)

# Global OPTIONS handler for all API routes
@app.options("/api/{path:path}")
async def handle_api_options(path: str):
    """Handle CORS preflight requests for all API routes"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRFToken, Cache-Control, Pragma, Origin, Referer, User-Agent",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Expose-Headers": "*",
            "Access-Control-Max-Age": "3600"
        }
    )

# Serve React app for specific client routes (client-side routing)
if frontend_build_path.exists():
    # Define specific routes that should serve the React app
    client_routes = [
        "/", "/login", "/register", "/guest-booking", "/book", 
        "/reschedule", "/edit-cleaning", "/payment", "/notes", 
        "/payment-history", "/upcoming", "/admin"
    ]
    
    for route in client_routes:
        @app.get(route)
        async def serve_react_app():
            index_path = frontend_build_path / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            else:
                raise HTTPException(status_code=404, detail="Frontend build not found")
    
    # Catch-all for other routes (but not API routes)
    @app.get("/{full_path:path}")
    async def serve_react_app_catchall(full_path: str):
        # Don't serve React app for API routes or static files
        if (full_path.startswith("api/") or 
            full_path == "health" or 
            full_path.startswith("admin/") or
            full_path.startswith("static/")):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (client-side routing)
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        else:
            raise HTTPException(status_code=404, detail="Frontend build not found")

# Cleaner Job Completion Endpoints
@api_router.get("/cleaner/jobs")
async def get_cleaner_jobs(cleaner_id: str):
    """Get all jobs assigned to a specific cleaner"""
    try:
        jobs = await db.bookings.find({
            "cleaner_id": cleaner_id,
            "status": {"$in": ["confirmed", "in_progress", "completed"]}
        }).to_list(1000)
        
        # Format job data for cleaner app
        formatted_jobs = []
        for job in jobs:
            formatted_jobs.append({
                "id": job.get("id"),
                "customer_id": job.get("customer_id"),
                "booking_date": job.get("booking_date"),
                "time_slot": job.get("time_slot"),
                "house_size": job.get("house_size"),
                "frequency": job.get("frequency"),
                "total_amount": job.get("total_amount"),
                "status": job.get("status"),
                "special_instructions": job.get("special_instructions"),
                "address": job.get("address", {}),
                "services": job.get("services", []),
                "a_la_carte_services": job.get("a_la_carte_services", []),
                "created_at": job.get("created_at"),
                "updated_at": job.get("updated_at")
            })
        
        return formatted_jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cleaner jobs: {str(e)}")

@api_router.patch("/cleaner/jobs/{job_id}/status")
async def update_job_status(job_id: str, status_data: dict):
    """Update job status (in_progress, completed)"""
    try:
        # Validate status
        valid_statuses = ["in_progress", "completed"]
        new_status = status_data.get("status")
        
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status. Must be 'in_progress' or 'completed'")
        
        # Update booking status
        update_data = {
            "status": new_status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add completion timestamp if marking as completed
        if new_status == "completed":
            update_data["completed_at"] = datetime.utcnow().isoformat()
            update_data["completion_notes"] = status_data.get("completion_notes", "")
        
        result = await db.bookings.update_one(
            {"id": job_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Update Google Calendar event if job is completed
        if new_status == "completed":
            booking = await db.bookings.find_one({"id": job_id})
            if booking and booking.get("calendar_event_id") and booking.get("cleaner_id"):
                cleaner = await db.cleaners.find_one({"id": booking["cleaner_id"]})
                if cleaner and cleaner.get("google_calendar_credentials"):
                    credentials = cleaner["google_calendar_credentials"]
                    service = calendar_service.create_service_from_credentials_dict(credentials)
                    
                    if service:
                        # Update calendar event to mark as completed
                        job_data = {
                            "job_id": job_id,
                            "status": "Completed",
                            "customer_name": f"Customer {booking.get('customer_id', '')[:8]}",
                            "address": f"{booking.get('address', {}).get('street', '')} {booking.get('address', {}).get('city', '')}",
                            "services": f"{booking.get('house_size', '')} - {booking.get('frequency', '')}",
                            "amount": booking.get("total_amount", 0),
                            "instructions": booking.get("special_instructions", "None")
                        }
                        
                        calendar_service.update_job_event(
                            service,
                            cleaner.get("google_calendar_id", "primary"),
                            booking["calendar_event_id"],
                            job_data
                        )
        
        return {"message": f"Job status updated to {new_status}", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job status: {str(e)}")

@api_router.patch("/cleaner/jobs/{job_id}/progress")
async def update_job_progress(job_id: str, progress_data: dict):
    """Update job progress and checklist items"""
    try:
        # Validate progress data
        completion_percentage = progress_data.get("completion_percentage", 0)
        if not 0 <= completion_percentage <= 100:
            raise HTTPException(status_code=400, detail="Completion percentage must be between 0 and 100")
        
        # Update booking with progress data
        update_data = {
            "progress": {
                "completion_percentage": completion_percentage,
                "current_task": progress_data.get("current_task", ""),
                "last_updated": datetime.utcnow().isoformat()
            },
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add checklist if provided
        if "checklist" in progress_data:
            update_data["checklist"] = progress_data["checklist"]
        
        result = await db.bookings.update_one(
            {"id": job_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": "Job progress updated", "job_id": job_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update job progress: {str(e)}")

@api_router.get("/cleaner/jobs/{job_id}")
async def get_job_details(job_id: str):
    """Get detailed information about a specific job"""
    try:
        job = await db.bookings.find_one({"id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get cleaner information if assigned
        cleaner_info = None
        if job.get("cleaner_id"):
            cleaner = await db.cleaners.find_one({"id": job["cleaner_id"]})
            if cleaner:
                cleaner_info = {
                    "id": cleaner.get("id"),
                    "first_name": cleaner.get("first_name"),
                    "last_name": cleaner.get("last_name"),
                    "email": cleaner.get("email"),
                    "phone": cleaner.get("phone")
                }
        
        # Format job details
        job_details = {
            "id": job.get("id"),
            "customer_id": job.get("customer_id"),
            "booking_date": job.get("booking_date"),
            "time_slot": job.get("time_slot"),
            "house_size": job.get("house_size"),
            "frequency": job.get("frequency"),
            "total_amount": job.get("total_amount"),
            "status": job.get("status"),
            "payment_status": job.get("payment_status"),
            "special_instructions": job.get("special_instructions"),
            "address": job.get("address", {}),
            "services": job.get("services", []),
            "a_la_carte_services": job.get("a_la_carte_services", []),
            "progress": job.get("progress", {}),
            "checklist": job.get("checklist", []),
            "completed_at": job.get("completed_at"),
            "completion_notes": job.get("completion_notes"),
            "cleaner": cleaner_info,
            "created_at": job.get("created_at"),
            "updated_at": job.get("updated_at")
        }
        
        return job_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job details: {str(e)}")

# Google Calendar OAuth Endpoints for Cleaners
@api_router.get("/calendar/auth/url")
async def get_calendar_auth_url():
    """Get Google Calendar OAuth authorization URL for cleaners"""
    try:
        from google_auth_oauthlib.flow import Flow
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=calendar_service.scopes
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Generate authorization URL
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return {"auth_url": auth_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@api_router.post("/calendar/auth/callback")
async def calendar_oauth_callback(request: GoogleCallbackRequest):
    """Handle Google Calendar OAuth callback and return credentials"""
    try:
        from google_auth_oauthlib.flow import Flow
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=calendar_service.scopes
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        
        # Exchange authorization code for credentials
        flow.fetch_token(code=request.code)
        credentials = flow.credentials
        
        # Convert credentials to dictionary
        credentials_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'id_token': credentials.id_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Validate credentials by creating a test service
        test_service = calendar_service.create_service_from_credentials_dict(credentials_dict)
        if not test_service:
            raise HTTPException(status_code=400, detail="Invalid calendar credentials")
        
        return {
            "message": "Calendar authentication successful",
            "credentials": credentials_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calendar authentication failed: {str(e)}")

@api_router.post("/create-checkout-session")
async def create_checkout_session(request: dict):
    """Create a Stripe checkout session for embedded checkout"""
    try:
        # Get booking ID from request
        booking_id = request.get('booking_id')
        if not booking_id:
            raise HTTPException(status_code=400, detail="Booking ID is required")
        
        # Get booking details
        booking = await db.bookings.find_one({"id": booking_id})
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Cleaning Service - {booking.get("service_type", "Standard Cleaning")}',
                        'description': f'Booking for {booking.get("customer", {}).get("name", "Customer")}',
                    },
                    'unit_amount': int(booking.get('total_amount', 0) * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{request.get("success_url", "http://localhost:3000")}/confirmation/{booking_id}',
            cancel_url=f'{request.get("cancel_url", "http://localhost:3000")}/payment/{booking_id}',
            metadata={
                'booking_id': booking_id,
                'customer_id': booking.get('customer_id', ''),
            }
        )
        
        return {"clientSecret": checkout_session.client_secret}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)