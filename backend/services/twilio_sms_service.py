"""
Twilio SMS Service for sending text message reminders
"""
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TwilioSMSService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning("Twilio credentials not configured. SMS functionality will be disabled.")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
    
    def is_configured(self) -> bool:
        """Check if Twilio is properly configured"""
        return self.client is not None
    
    def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """
        Send SMS message to a phone number
        
        Args:
            to_phone: Recipient phone number (with country code, e.g., +1234567890)
            message: SMS message content
            
        Returns:
            Dict with success status and message details
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Twilio not configured",
                "message": "SMS service is not available"
            }
        
        try:
            # Clean phone number (remove any non-digit characters except +)
            clean_phone = ''.join(c for c in to_phone if c.isdigit() or c == '+')
            if not clean_phone.startswith('+'):
                clean_phone = '+1' + clean_phone  # Default to US if no country code
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=clean_phone
            )
            
            logger.info(f"SMS sent successfully to {clean_phone}. SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_sid": message_obj.sid,
                "to": clean_phone,
                "status": message_obj.status,
                "message": "SMS sent successfully"
            }
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send SMS"
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS to {to_phone}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send SMS"
            }
    
    def format_phone_number(self, phone: str) -> str:
        """
        Format phone number for Twilio (ensure it has country code)
        
        Args:
            phone: Raw phone number
            
        Returns:
            Formatted phone number with country code
        """
        # Remove all non-digit characters
        digits = ''.join(c for c in phone if c.isdigit())
        
        # If it starts with 1 and is 11 digits, it's already US format
        if len(digits) == 11 and digits.startswith('1'):
            return '+' + digits
        # If it's 10 digits, assume US and add +1
        elif len(digits) == 10:
            return '+1' + digits
        # If it already has country code, return as is
        elif phone.startswith('+'):
            return phone
        # Default to US format
        else:
            return '+1' + digits[-10:] if len(digits) >= 10 else phone

# Global instance
sms_service = TwilioSMSService()
