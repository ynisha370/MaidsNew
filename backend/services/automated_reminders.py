"""
Automated Email Reminder System
This service handles automated email reminders for upcoming appointments
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from services.email_service import email_service
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedReminderService:
    def __init__(self, db_client: AsyncIOMotorClient):
        self.db = db_client
        self.email_service = email_service
        
    async def send_day_before_reminders(self) -> Dict[str, Any]:
        """
        Send reminders for appointments tomorrow
        """
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Get bookings for tomorrow
            bookings = await self.db.bookings.find({
                "booking_date": tomorrow,
                "status": {"$in": ["confirmed", "pending"]}
            }).to_list(1000)
            
            results = {
                "date": tomorrow,
                "total_bookings": len(bookings),
                "emails_sent": 0,
                "emails_failed": 0,
                "errors": []
            }
            
            for booking in bookings:
                try:
                    success = await self._send_booking_reminder(booking, "day_before")
                    if success:
                        results["emails_sent"] += 1
                    else:
                        results["emails_failed"] += 1
                        results["errors"].append({
                            "booking_id": booking.get("id"),
                            "error": "Failed to send day-before reminder"
                        })
                except Exception as e:
                    results["emails_failed"] += 1
                    results["errors"].append({
                        "booking_id": booking.get("id"),
                        "error": str(e)
                    })
                    logger.error(f"Error sending day-before reminder for booking {booking.get('id')}: {e}")
            
            logger.info(f"Day-before reminders: {results['emails_sent']} sent, {results['emails_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in send_day_before_reminders: {e}")
            return {"error": str(e)}
    
    async def send_week_before_reminders(self) -> Dict[str, Any]:
        """
        Send reminders for appointments next week
        """
        try:
            next_week = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            # Get bookings for next week
            bookings = await self.db.bookings.find({
                "booking_date": next_week,
                "status": {"$in": ["confirmed", "pending"]}
            }).to_list(1000)
            
            results = {
                "date": next_week,
                "total_bookings": len(bookings),
                "emails_sent": 0,
                "emails_failed": 0,
                "errors": []
            }
            
            for booking in bookings:
                try:
                    success = await self._send_booking_reminder(booking, "week_before")
                    if success:
                        results["emails_sent"] += 1
                    else:
                        results["emails_failed"] += 1
                        results["errors"].append({
                            "booking_id": booking.get("id"),
                            "error": "Failed to send week-before reminder"
                        })
                except Exception as e:
                    results["emails_failed"] += 1
                    results["errors"].append({
                        "booking_id": booking.get("id"),
                        "error": str(e)
                    })
                    logger.error(f"Error sending week-before reminder for booking {booking.get('id')}: {e}")
            
            logger.info(f"Week-before reminders: {results['emails_sent']} sent, {results['emails_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in send_week_before_reminders: {e}")
            return {"error": str(e)}
    
    async def send_confirmation_reminders(self) -> Dict[str, Any]:
        """
        Send confirmation emails for newly confirmed bookings
        """
        try:
            # Get bookings confirmed in the last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            bookings = await self.db.bookings.find({
                "status": "confirmed",
                "updated_at": {"$gte": one_hour_ago.isoformat()},
                "confirmation_email_sent": {"$ne": True}
            }).to_list(1000)
            
            results = {
                "total_bookings": len(bookings),
                "emails_sent": 0,
                "emails_failed": 0,
                "errors": []
            }
            
            for booking in bookings:
                try:
                    success = await self._send_booking_reminder(booking, "confirmation")
                    if success:
                        # Mark confirmation email as sent
                        await self.db.bookings.update_one(
                            {"id": booking["id"]},
                            {"$set": {"confirmation_email_sent": True}}
                        )
                        results["emails_sent"] += 1
                    else:
                        results["emails_failed"] += 1
                        results["errors"].append({
                            "booking_id": booking.get("id"),
                            "error": "Failed to send confirmation email"
                        })
                except Exception as e:
                    results["emails_failed"] += 1
                    results["errors"].append({
                        "booking_id": booking.get("id"),
                        "error": str(e)
                    })
                    logger.error(f"Error sending confirmation email for booking {booking.get('id')}: {e}")
            
            logger.info(f"Confirmation emails: {results['emails_sent']} sent, {results['emails_failed']} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in send_confirmation_reminders: {e}")
            return {"error": str(e)}
    
    async def _send_booking_reminder(self, booking: Dict[str, Any], reminder_type: str) -> bool:
        """
        Send a reminder email for a specific booking
        """
        try:
            # Get customer email
            customer_email = None
            if booking.get('customer'):
                customer_email = booking['customer'].get('email')
            elif booking.get('user_id'):
                # Try to get email from user data
                user = await self.db.users.find_one({"id": booking['user_id']})
                if user:
                    customer_email = user.get('email')
            
            if not customer_email:
                logger.warning(f"No customer email found for booking {booking.get('id')}")
                return False
            
            # Send email reminder
            return self.email_service.send_booking_reminder(booking, reminder_type)
            
        except Exception as e:
            logger.error(f"Error in _send_booking_reminder: {e}")
            return False
    
    async def run_daily_reminders(self) -> Dict[str, Any]:
        """
        Run all daily reminder tasks
        """
        try:
            logger.info("Starting daily reminder tasks...")
            
            # Run all reminder types
            day_before_results = await self.send_day_before_reminders()
            week_before_results = await self.send_week_before_reminders()
            confirmation_results = await self.send_confirmation_reminders()
            
            # Log results
            total_sent = (
                day_before_results.get("emails_sent", 0) +
                week_before_results.get("emails_sent", 0) +
                confirmation_results.get("emails_sent", 0)
            )
            
            total_failed = (
                day_before_results.get("emails_failed", 0) +
                week_before_results.get("emails_failed", 0) +
                confirmation_results.get("emails_failed", 0)
            )
            
            logger.info(f"Daily reminders completed: {total_sent} sent, {total_failed} failed")
            
            return {
                "day_before": day_before_results,
                "week_before": week_before_results,
                "confirmation": confirmation_results,
                "summary": {
                    "total_sent": total_sent,
                    "total_failed": total_failed
                }
            }
            
        except Exception as e:
            logger.error(f"Error in run_daily_reminders: {e}")
            return {"error": str(e)}

# Scheduled task runner
async def run_scheduled_reminders():
    """
    Function to be called by a scheduler (like cron or APScheduler)
    """
    try:
        # Get database connection
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DB_NAME", "maidsofcyfair")
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Create reminder service
        reminder_service = AutomatedReminderService(db)
        
        # Run daily reminders
        results = await reminder_service.run_daily_reminders()
        
        # Log results
        logger.info(f"Scheduled reminders completed: {results}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in run_scheduled_reminders: {e}")
        return {"error": str(e)}
    finally:
        client.close()

# Example usage for testing
async def test_reminders():
    """
    Test function to run reminders manually
    """
    results = await run_scheduled_reminders()
    print(f"Reminder results: {results}")

if __name__ == "__main__":
    # Run test reminders
    asyncio.run(test_reminders())
