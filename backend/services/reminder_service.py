"""
SMS Reminder Service for customizable text message reminders
"""
import os
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import logging
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorDatabase
from .twilio_sms_service import sms_service

logger = logging.getLogger(__name__)

class ReminderType(str, Enum):
    BOOKING_CONFIRMATION = "booking_confirmation"
    DAY_BEFORE_REMINDER = "day_before_reminder"
    HOUR_BEFORE_REMINDER = "hour_before_reminder"
    CLEANER_ON_THE_WAY = "cleaner_on_the_way"
    SERVICE_COMPLETED = "service_completed"
    CUSTOM = "custom"

class ReminderTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: ReminderType
    template: str
    is_active: bool = True
    send_timing: Optional[str] = None  # e.g., "24h", "1h", "immediate"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ReminderLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    customer_phone: str
    template_id: str
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str  # "sent", "failed", "pending"
    twilio_sid: Optional[str] = None
    error_message: Optional[str] = None

class ReminderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sms_service = sms_service
        
    async def get_default_templates(self) -> List[ReminderTemplate]:
        """Get default reminder templates"""
        return [
            ReminderTemplate(
                name="Booking Confirmation",
                type=ReminderType.BOOKING_CONFIRMATION,
                template="Hi {customer_name}! Your cleaning service is confirmed for {booking_date} at {time_slot}. We'll see you soon! - Maids of CyFair",
                send_timing="immediate",
                is_active=True
            ),
            ReminderTemplate(
                name="Day Before Reminder",
                type=ReminderType.DAY_BEFORE_REMINDER,
                template="Reminder: Your cleaning service is tomorrow ({booking_date}) at {time_slot}. Please ensure access to your home. - Maids of CyFair",
                send_timing="24h",
                is_active=True
            ),
            ReminderTemplate(
                name="Hour Before Reminder",
                type=ReminderType.HOUR_BEFORE_REMINDER,
                template="Your cleaner will arrive in about 1 hour for your {booking_date} service. Please ensure access to your home. - Maids of CyFair",
                send_timing="1h",
                is_active=True
            ),
            ReminderTemplate(
                name="Cleaner On The Way",
                type=ReminderType.CLEANER_ON_THE_WAY,
                template="Your cleaner is on the way! ETA: {eta}. Please ensure access to your home. - Maids of CyFair",
                send_timing="immediate",
                is_active=True
            ),
            ReminderTemplate(
                name="Service Completed",
                type=ReminderType.SERVICE_COMPLETED,
                template="Thank you for choosing Maids of CyFair! Your cleaning service is complete. We hope you're satisfied with our work. - Maids of CyFair",
                send_timing="immediate",
                is_active=True
            )
        ]
    
    async def initialize_default_templates(self):
        """Initialize default templates in the database"""
        try:
            # Check if templates already exist
            existing_count = await self.db.reminder_templates.count_documents({})
            if existing_count > 0:
                logger.info("Reminder templates already exist, skipping initialization")
                return
            
            default_templates = await self.get_default_templates()
            for template in default_templates:
                template_dict = template.dict()
                await self.db.reminder_templates.insert_one(template_dict)
            
            logger.info(f"Initialized {len(default_templates)} default reminder templates")
        except Exception as e:
            logger.error(f"Error initializing default templates: {str(e)}")
    
    async def get_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all reminder templates"""
        try:
            query = {"is_active": True} if active_only else {}
            cursor = self.db.reminder_templates.find(query).sort("created_at", -1)
            templates = await cursor.to_list(length=None)
            return templates
        except Exception as e:
            logger.error(f"Error fetching templates: {str(e)}")
            return []
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID"""
        try:
            template = await self.db.reminder_templates.find_one({"id": template_id})
            return template
        except Exception as e:
            logger.error(f"Error fetching template {template_id}: {str(e)}")
            return None
    
    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new reminder template"""
        try:
            template = ReminderTemplate(**template_data)
            template_dict = template.dict()
            result = await self.db.reminder_templates.insert_one(template_dict)
            
            if result.inserted_id:
                logger.info(f"Created template: {template.name}")
                return {"success": True, "template_id": template.id, "message": "Template created successfully"}
            else:
                return {"success": False, "message": "Failed to create template"}
                
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            return {"success": False, "message": f"Error creating template: {str(e)}"}
    
    async def update_template(self, template_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing template"""
        try:
            update_data["updated_at"] = datetime.utcnow()
            result = await self.db.reminder_templates.update_one(
                {"id": template_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated template: {template_id}")
                return {"success": True, "message": "Template updated successfully"}
            else:
                return {"success": False, "message": "Template not found or no changes made"}
                
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {str(e)}")
            return {"success": False, "message": f"Error updating template: {str(e)}"}
    
    async def delete_template(self, template_id: str) -> Dict[str, Any]:
        """Delete a template (soft delete by setting is_active to False)"""
        try:
            result = await self.db.reminder_templates.update_one(
                {"id": template_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Deleted template: {template_id}")
                return {"success": True, "message": "Template deleted successfully"}
            else:
                return {"success": False, "message": "Template not found"}
                
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {str(e)}")
            return {"success": False, "message": f"Error deleting template: {str(e)}"}
    
    def format_message(self, template: str, booking_data: Dict[str, Any]) -> str:
        """Format template message with booking data"""
        try:
            # Extract customer info
            customer_name = booking_data.get('customer', {}).get('first_name', 'Valued Customer')
            if booking_data.get('customer', {}).get('last_name'):
                customer_name += f" {booking_data['customer']['last_name']}"
            
            # Format date
            booking_date = booking_data.get('booking_date', '')
            if booking_date:
                try:
                    date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%A, %B %d, %Y')
                except:
                    formatted_date = booking_date
            else:
                formatted_date = 'your scheduled date'
            
            # Format time
            time_slot = booking_data.get('time_slot', 'your scheduled time')
            
            # Additional context
            house_size = booking_data.get('house_size', '')
            services = booking_data.get('services', [])
            service_names = [service.get('name', '') for service in services if service.get('name')]
            service_list = ', '.join(service_names) if service_names else 'cleaning service'
            
            # Replace placeholders
            formatted_message = template.format(
                customer_name=customer_name,
                booking_date=formatted_date,
                time_slot=time_slot,
                house_size=house_size,
                services=service_list,
                eta=booking_data.get('eta', 'shortly'),
                company_name='Maids of CyFair'
            )
            
            return formatted_message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return template  # Return original template if formatting fails
    
    async def send_reminder(self, booking_id: str, template_id: str, custom_message: Optional[str] = None) -> Dict[str, Any]:
        """Send a reminder for a specific booking"""
        try:
            # Get booking data
            booking = await self.db.bookings.find_one({"id": booking_id})
            if not booking:
                return {"success": False, "message": "Booking not found"}
            
            # Get template
            template = await self.get_template(template_id)
            if not template:
                return {"success": False, "message": "Template not found"}
            
            # Format message
            if custom_message:
                message = custom_message
            else:
                message = self.format_message(template['template'], booking)
            
            # Get customer phone
            customer_phone = booking.get('customer', {}).get('phone')
            if not customer_phone:
                return {"success": False, "message": "Customer phone number not found"}
            
            # Send SMS
            sms_result = self.sms_service.send_sms(customer_phone, message)
            
            # Log the reminder
            reminder_log = ReminderLog(
                booking_id=booking_id,
                customer_phone=customer_phone,
                template_id=template_id,
                message=message,
                status="sent" if sms_result["success"] else "failed",
                twilio_sid=sms_result.get("message_sid"),
                error_message=sms_result.get("error")
            )
            
            await self.db.reminder_logs.insert_one(reminder_log.dict())
            
            if sms_result["success"]:
                logger.info(f"Reminder sent successfully for booking {booking_id}")
                return {"success": True, "message": "Reminder sent successfully", "log_id": reminder_log.id}
            else:
                logger.error(f"Failed to send reminder for booking {booking_id}: {sms_result.get('error')}")
                return {"success": False, "message": f"Failed to send reminder: {sms_result.get('error')}"}
                
        except Exception as e:
            logger.error(f"Error sending reminder for booking {booking_id}: {str(e)}")
            return {"success": False, "message": f"Error sending reminder: {str(e)}"}
    
    async def get_reminder_logs(self, booking_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get reminder logs"""
        try:
            query = {"booking_id": booking_id} if booking_id else {}
            cursor = self.db.reminder_logs.find(query).sort("sent_at", -1).limit(limit)
            logs = await cursor.to_list(length=None)
            return logs
        except Exception as e:
            logger.error(f"Error fetching reminder logs: {str(e)}")
            return []
