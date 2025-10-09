"""
Automatic Reminder Scheduler Service
Handles scheduling and sending of automatic reminders based on booking dates
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
from .reminder_service import ReminderService, ReminderType

logger = logging.getLogger(__name__)

class ReminderScheduler:
    def __init__(self, db: AsyncIOMotorDatabase, reminder_service: ReminderService):
        self.db = db
        self.reminder_service = reminder_service
        self.is_running = False
        self.task = None
    
    def parse_time_slot(self, time_slot: str) -> Optional[Tuple[int, int]]:
        """
        Parse time slot string and return (hour, minute) in 24-hour format
        Handles various formats like:
        - "9:00 AM - 11:00 AM"
        - "2:30 PM - 4:30 PM"
        - "10:00 AM"
        - "14:30" (24-hour format)
        """
        if not time_slot:
            return None
        
        try:
            # Extract the start time (before the dash)
            start_time_str = time_slot.split(" - ")[0].strip()
            
            # Handle 24-hour format (e.g., "14:30")
            if re.match(r'^\d{1,2}:\d{2}$', start_time_str):
                hour, minute = map(int, start_time_str.split(':'))
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return (hour, minute)
                return None
            
            # Handle 12-hour format (e.g., "2:30 PM", "10:00 AM")
            time_match = re.match(r'^(\d{1,2}):(\d{2})\s*(AM|PM)$', start_time_str.upper())
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                period = time_match.group(3)
                
                # Validate hour for 12-hour format (1-12)
                if hour < 1 or hour > 12:
                    return None
                
                # Validate minute
                if minute < 0 or minute > 59:
                    return None
                
                # Convert to 24-hour format
                if period == 'AM':
                    if hour == 12:
                        hour = 0
                elif period == 'PM':
                    if hour != 12:
                        hour += 12
                
                # Validate final hour
                if 0 <= hour <= 23:
                    return (hour, minute)
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing time slot '{time_slot}': {str(e)}")
            return None
    
    async def start_scheduler(self):
        """Start the automatic reminder scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Reminder scheduler started")
    
    async def stop_scheduler(self):
        """Stop the automatic reminder scheduler"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Reminder scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop - runs every 5 minutes"""
        while self.is_running:
            try:
                await self._process_reminders()
                await asyncio.sleep(300)  # Wait 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _process_reminders(self):
        """Process all pending reminders"""
        try:
            # Get all active templates
            templates = await self.reminder_service.get_templates(active_only=True)
            template_map = {t['type']: t for t in templates}
            
            # Process different types of reminders
            await self._process_day_before_reminders(template_map)
            await self._process_hour_before_reminders(template_map)
            await self._process_booking_confirmations(template_map)
            
        except Exception as e:
            logger.error(f"Error processing reminders: {str(e)}")
    
    async def _process_day_before_reminders(self, template_map: Dict[str, Any]):
        """Process day-before reminders"""
        try:
            # Get bookings for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            bookings = await self.db.bookings.find({
                "booking_date": tomorrow_str,
                "status": {"$in": ["confirmed", "pending"]}
            }).to_list(length=None)
            
            template = template_map.get(ReminderType.DAY_BEFORE_REMINDER)
            if not template:
                return
            
            for booking in bookings:
                # Check if reminder already sent
                existing_log = await self.db.reminder_logs.find_one({
                    "booking_id": booking["id"],
                    "template_id": template["id"],
                    "status": "sent"
                })
                
                if not existing_log:
                    # Send day-before reminder
                    result = await self.reminder_service.send_reminder(
                        booking["id"], 
                        template["id"]
                    )
                    if result["success"]:
                        logger.info(f"Day-before reminder sent for booking {booking['id']}")
                    else:
                        logger.error(f"Failed to send day-before reminder for booking {booking['id']}: {result['message']}")
                        
        except Exception as e:
            logger.error(f"Error processing day-before reminders: {str(e)}")
    
    async def _process_hour_before_reminders(self, template_map: Dict[str, Any]):
        """Process hour-before reminders"""
        try:
            # Get bookings for today within the next 2 hours
            now = datetime.now()
            two_hours_from_now = now + timedelta(hours=2)
            
            # Get today's bookings
            today_str = now.strftime('%Y-%m-%d')
            bookings = await self.db.bookings.find({
                "booking_date": today_str,
                "status": {"$in": ["confirmed", "pending"]}
            }).to_list(length=None)
            
            template = template_map.get(ReminderType.HOUR_BEFORE_REMINDER)
            if not template:
                return
            
            for booking in bookings:
                # Parse time slot to determine if it's within the next 2 hours
                time_slot = booking.get("time_slot", "")
                if not time_slot:
                    continue
                
                # Use improved time parsing
                try:
                    time_result = self.parse_time_slot(time_slot)
                    if time_result is None:
                        logger.warning(f"Could not parse time slot for booking {booking['id']}: {time_slot}")
                        continue
                    
                    hour, minute = time_result
                    
                    # Create datetime for today with the booking time
                    booking_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Check if booking is within the next 2 hours
                    if now <= booking_datetime <= two_hours_from_now:
                        # Check if reminder already sent
                        existing_log = await self.db.reminder_logs.find_one({
                            "booking_id": booking["id"],
                            "template_id": template["id"],
                            "status": "sent"
                        })
                        
                        if not existing_log:
                            # Send hour-before reminder
                            result = await self.reminder_service.send_reminder(
                                booking["id"], 
                                template["id"]
                            )
                            if result["success"]:
                                logger.info(f"Hour-before reminder sent for booking {booking['id']}")
                            else:
                                logger.error(f"Failed to send hour-before reminder for booking {booking['id']}: {result['message']}")
                                
                except Exception as e:
                    logger.error(f"Error parsing time slot for booking {booking['id']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing hour-before reminders: {str(e)}")
    
    async def _process_booking_confirmations(self, template_map: Dict[str, Any]):
        """Process booking confirmation reminders for new bookings"""
        try:
            # Get bookings created in the last 5 minutes that haven't had confirmation sent
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            
            bookings = await self.db.bookings.find({
                "created_at": {"$gte": five_minutes_ago},
                "status": {"$in": ["confirmed", "pending"]}
            }).to_list(length=None)
            
            template = template_map.get(ReminderType.BOOKING_CONFIRMATION)
            if not template:
                return
            
            for booking in bookings:
                # Check if confirmation already sent
                existing_log = await self.db.reminder_logs.find_one({
                    "booking_id": booking["id"],
                    "template_id": template["id"],
                    "status": "sent"
                })
                
                if not existing_log:
                    # Send booking confirmation
                    result = await self.reminder_service.send_reminder(
                        booking["id"], 
                        template["id"]
                    )
                    if result["success"]:
                        logger.info(f"Booking confirmation sent for booking {booking['id']}")
                    else:
                        logger.error(f"Failed to send booking confirmation for booking {booking['id']}: {result['message']}")
                        
        except Exception as e:
            logger.error(f"Error processing booking confirmations: {str(e)}")
    
    async def send_immediate_reminder(self, booking_id: str, reminder_type: ReminderType, custom_message: Optional[str] = None) -> Dict[str, Any]:
        """Send an immediate reminder for a specific booking"""
        try:
            # Get the appropriate template
            templates = await self.reminder_service.get_templates(active_only=True)
            template = next((t for t in templates if t['type'] == reminder_type.value), None)
            
            if not template:
                return {"success": False, "message": f"No active template found for {reminder_type.value}"}
            
            # Send the reminder
            result = await self.reminder_service.send_reminder(
                booking_id, 
                template["id"], 
                custom_message
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending immediate reminder: {str(e)}")
            return {"success": False, "message": f"Error sending reminder: {str(e)}"}
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get the current status of the scheduler"""
        return {
            "is_running": self.is_running,
            "last_check": datetime.now().isoformat(),
            "status": "active" if self.is_running else "inactive"
        }
