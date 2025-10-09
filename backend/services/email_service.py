"""
Amazon SES Email Service for sending booking reminders and notifications
"""

import boto3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize SES client with AWS credentials"""
        self.ses_client = boto3.client(
            'ses',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@maidsofcyfair.com')
        self.from_name = os.getenv('FROM_NAME', 'Maids of CyFair')
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send a single email using SES
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': html_content,
                        'Charset': 'UTF-8'
                    }
                }
            }
            
            # Add text content if provided
            if text_content:
                message['Body']['Text'] = {
                    'Data': text_content,
                    'Charset': 'UTF-8'
                }
            
            response = self.ses_client.send_email(
                Source=f'{self.from_name} <{self.from_email}>',
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            logger.info(f"Email sent successfully to {to_email}. MessageId: {response['MessageId']}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False
    
    def send_bulk_emails(self, email_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send multiple emails in batch
        
        Args:
            email_list: List of dictionaries containing email data
                       Each dict should have: to_email, subject, html_content, text_content (optional)
        
        Returns:
            Dict with success/failure counts and details
        """
        results = {
            'total': len(email_list),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for email_data in email_list:
            success = self.send_email(
                to_email=email_data['to_email'],
                subject=email_data['subject'],
                html_content=email_data['html_content'],
                text_content=email_data.get('text_content')
            )
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'email': email_data['to_email'],
                    'error': 'Failed to send email'
                })
        
        return results
    
    def create_reminder_template(self, booking_data: Dict[str, Any], reminder_type: str = "upcoming") -> Dict[str, str]:
        """
        Create email template for booking reminders
        
        Args:
            booking_data: Booking information
            reminder_type: Type of reminder (upcoming, day_before, week_before, etc.)
        
        Returns:
            Dict with subject, html_content, and text_content
        """
        customer_name = booking_data.get('customer', {}).get('first_name', 'Valued Customer')
        booking_date = booking_data.get('booking_date', '')
        time_slot = booking_data.get('time_slot', '')
        total_amount = booking_data.get('total_amount', 0)
        address = booking_data.get('address', {})
        
        # Format date for display
        try:
            date_obj = datetime.strptime(booking_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%A, %B %d, %Y')
        except:
            formatted_date = booking_date
        
        # Format address
        address_str = ""
        if address:
            address_parts = []
            if address.get('street'):
                address_parts.append(address['street'])
            if address.get('city'):
                address_parts.append(address['city'])
            if address.get('state'):
                address_parts.append(address['state'])
            if address.get('zip_code'):
                address_parts.append(address['zip_code'])
            address_str = ", ".join(address_parts)
        
        # Create subject based on reminder type
        subjects = {
            "upcoming": f"Upcoming Cleaning Appointment - {formatted_date}",
            "day_before": f"Reminder: Your Cleaning is Tomorrow - {formatted_date}",
            "week_before": f"Your Cleaning Appointment is Next Week - {formatted_date}",
            "confirmation": f"Cleaning Appointment Confirmed - {formatted_date}",
            "cancelled": f"Cleaning Appointment Cancelled - {formatted_date}"
        }
        
        subject = subjects.get(reminder_type, f"Cleaning Appointment Reminder - {formatted_date}")
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{subject}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 3px solid #2c5aa0;
                    padding-bottom: 20px;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c5aa0;
                    margin-bottom: 10px;
                }}
                .appointment-details {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    padding: 8px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                }}
                .detail-value {{
                    color: #6c757d;
                }}
                .highlight {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-left: 4px solid #2196f3;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #2c5aa0;
                    color: white;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .reminder-type {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Maids of CyFair</div>
                    <p>Professional Cleaning Services</p>
                </div>
                
                <div class="reminder-type">
                    <strong>📅 Appointment Reminder</strong>
                </div>
                
                <h2>Hello {customer_name}!</h2>
                
                <p>This is a friendly reminder about your upcoming cleaning appointment with Maids of CyFair.</p>
                
                <div class="appointment-details">
                    <h3>Appointment Details</h3>
                    <div class="detail-row">
                        <span class="detail-label">Date:</span>
                        <span class="detail-value">{formatted_date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Time:</span>
                        <span class="detail-value">{time_slot}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Total Amount:</span>
                        <span class="detail-value">${total_amount:.2f}</span>
                    </div>
                    {f'<div class="detail-row"><span class="detail-label">Address:</span><span class="detail-value">{address_str}</span></div>' if address_str else ''}
                </div>
                
                <div class="highlight">
                    <h4>📋 What to Expect:</h4>
                    <ul>
                        <li>Our professional cleaning team will arrive at your scheduled time</li>
                        <li>Please ensure access to your home</li>
                        <li>Secure any valuables before our arrival</li>
                        <li>Our team will provide all cleaning supplies and equipment</li>
                    </ul>
                </div>
                
                <p>If you need to reschedule or have any questions, please contact us as soon as possible.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="tel:+17135551234" class="button">Call Us: (713) 555-1234</a>
                    <a href="mailto:info@maidsofcyfair.com" class="button">Email Us</a>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing Maids of CyFair!</p>
                    <p>Professional • Reliable • Trusted</p>
                    <p><small>This is an automated message. Please do not reply to this email.</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text content
        text_content = f"""
        Maids of CyFair - Appointment Reminder
        
        Hello {customer_name}!
        
        This is a friendly reminder about your upcoming cleaning appointment.
        
        Appointment Details:
        - Date: {formatted_date}
        - Time: {time_slot}
        - Total Amount: ${total_amount:.2f}
        {f"- Address: {address_str}" if address_str else ""}
        
        What to Expect:
        - Our professional cleaning team will arrive at your scheduled time
        - Please ensure access to your home
        - Secure any valuables before our arrival
        - Our team will provide all cleaning supplies and equipment
        
        If you need to reschedule or have any questions, please contact us:
        - Phone: (713) 555-1234
        - Email: info@maidsofcyfair.com
        
        Thank you for choosing Maids of CyFair!
        Professional • Reliable • Trusted
        
        This is an automated message. Please do not reply to this email.
        """
        
        return {
            'subject': subject,
            'html_content': html_content,
            'text_content': text_content
        }
    
    def send_booking_reminder(self, booking_data: Dict[str, Any], reminder_type: str = "upcoming") -> bool:
        """
        Send a booking reminder email
        
        Args:
            booking_data: Booking information
            reminder_type: Type of reminder
        
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Get customer email
            customer_email = None
            if booking_data.get('customer'):
                customer_email = booking_data['customer'].get('email')
            elif booking_data.get('user_id'):
                # If it's a registered user, we might need to fetch their email from users collection
                # For now, we'll assume the email is in the booking data
                customer_email = booking_data.get('customer_email')
            
            if not customer_email:
                logger.error(f"No customer email found for booking {booking_data.get('id', 'unknown')}")
                return False
            
            # Create email template
            email_template = self.create_reminder_template(booking_data, reminder_type)
            
            # Send email
            return self.send_email(
                to_email=customer_email,
                subject=email_template['subject'],
                html_content=email_template['html_content'],
                text_content=email_template['text_content']
            )
        
        except Exception as e:
            logger.error(f"Error sending booking reminder: {e}")
            return False
    
    def send_cleaner_pending_approval_email(self, cleaner_email: str, cleaner_name: str) -> bool:
        """Send email to cleaner after registration confirming pending approval"""
        subject = "Application Received - Maids of CyFair"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2196F3;">Application Received!</h2>
                    <p>Hi {cleaner_name},</p>
                    <p>Thank you for applying to join our team at Maids of CyFair!</p>
                    <p>Your application has been received and is currently under review by our admin team.</p>
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Our team will review your application within 24-48 hours</li>
                        <li>You will receive an email notification once your application is approved</li>
                        <li>After approval, you can log in to access your cleaner dashboard</li>
                    </ul>
                    <p>If you have any questions, please contact us at support@maidsofcyfair.com</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {cleaner_name}, Your application to Maids of CyFair has been received and is under review. You will receive an email once approved."
        
        return self.send_email(cleaner_email, subject, html_content, text_content)
    
    def send_cleaner_approved_email(self, cleaner_email: str, cleaner_name: str, login_url: str) -> bool:
        """Send email to cleaner after admin approval"""
        subject = "Welcome to Maids of CyFair - Application Approved!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #4CAF50;">🎉 Congratulations!</h2>
                    <p>Hi {cleaner_name},</p>
                    <p>Great news! Your application has been approved by our admin team.</p>
                    <p>You can now log in to your cleaner dashboard to:</p>
                    <ul>
                        <li>View assigned cleaning jobs</li>
                        <li>Clock in/out of jobs</li>
                        <li>Update ETAs for customers</li>
                        <li>Track your earnings</li>
                        <li>Manage your schedule</li>
                    </ul>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{login_url}" style="background-color: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Login to Dashboard</a>
                    </div>
                    <p>Welcome to the team!</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {cleaner_name}, Congratulations! Your application has been approved. You can now log in at {login_url}"
        
        return self.send_email(cleaner_email, subject, html_content, text_content)
    
    def send_cleaner_rejected_email(self, cleaner_email: str, cleaner_name: str, reason: str = "") -> bool:
        """Send email to cleaner after admin rejection"""
        subject = "Application Update - Maids of CyFair"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #666;">Application Update</h2>
                    <p>Hi {cleaner_name},</p>
                    <p>Thank you for your interest in joining Maids of CyFair.</p>
                    <p>After careful consideration, we are unable to move forward with your application at this time.</p>
                    {reason_text}
                    <p>We appreciate your interest and wish you the best in your future endeavors.</p>
                    <p>If you have any questions, please contact us at support@maidsofcyfair.com</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {cleaner_name}, Thank you for applying to Maids of CyFair. We are unable to move forward with your application at this time."
        
        return self.send_email(cleaner_email, subject, html_content, text_content)
    
    def send_job_assigned_email(self, cleaner_email: str, cleaner_name: str, job_details: dict) -> bool:
        """Send email to cleaner when a new job is assigned"""
        subject = f"New Job Assigned - {job_details.get('booking_date', 'TBD')}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2196F3;">New Job Assigned</h2>
                    <p>Hi {cleaner_name},</p>
                    <p>You have been assigned a new cleaning job:</p>
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Date:</strong> {job_details.get('booking_date', 'TBD')}</p>
                        <p><strong>Time:</strong> {job_details.get('time_slot', 'TBD')}</p>
                        <p><strong>Service:</strong> {job_details.get('house_size', '')} - {job_details.get('frequency', '')}</p>
                        <p><strong>Amount:</strong> ${job_details.get('total_amount', 0)}</p>
                        <p><strong>Address:</strong> {job_details.get('address_text', 'See dashboard')}</p>
                    </div>
                    <p>Please log in to your dashboard to view full details and prepare for the job.</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {cleaner_name}, You have been assigned a new job on {job_details.get('booking_date', 'TBD')} at {job_details.get('time_slot', 'TBD')}. Check your dashboard for details."
        
        return self.send_email(cleaner_email, subject, html_content, text_content)
    
    def send_job_reassigned_email(self, cleaner_email: str, cleaner_name: str, job_details: dict, reason: str = "") -> bool:
        """Send email to cleaner when a job is removed/reassigned"""
        subject = f"Job Reassignment Notification - {job_details.get('booking_date', 'TBD')}"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #FF9800;">Job Reassignment</h2>
                    <p>Hi {cleaner_name},</p>
                    <p>The following job has been reassigned to another cleaner:</p>
                    <div style="background-color: #fff3e0; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Date:</strong> {job_details.get('booking_date', 'TBD')}</p>
                        <p><strong>Time:</strong> {job_details.get('time_slot', 'TBD')}</p>
                        <p><strong>Service:</strong> {job_details.get('house_size', '')} - {job_details.get('frequency', '')}</p>
                        <p><strong>Address:</strong> {job_details.get('address_text', 'See dashboard')}</p>
                    </div>
                    {reason_text}
                    <p>This job is no longer on your schedule. Please check your dashboard for updated assignments.</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {cleaner_name}, The job on {job_details.get('booking_date', 'TBD')} has been reassigned to another cleaner. Check your dashboard for updates."
        
        return self.send_email(cleaner_email, subject, html_content, text_content)
    
    def send_cleaner_changed_email(self, customer_email: str, customer_name: str, old_cleaner: str, new_cleaner: str, booking_details: dict) -> bool:
        """Send email to customer when their assigned cleaner changes"""
        subject = f"Cleaner Assignment Update - {booking_details.get('booking_date', 'TBD')}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px;">
                    <h2 style="color: #2196F3;">Cleaner Assignment Update</h2>
                    <p>Hi {customer_name},</p>
                    <p>We wanted to inform you of a change to your upcoming cleaning appointment:</p>
                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Date:</strong> {booking_details.get('booking_date', 'TBD')}</p>
                        <p><strong>Time:</strong> {booking_details.get('time_slot', 'TBD')}</p>
                        <p><strong>Previous Cleaner:</strong> {old_cleaner}</p>
                        <p><strong>New Cleaner:</strong> {new_cleaner}</p>
                    </div>
                    <p>Your new cleaner {new_cleaner} is experienced and will provide the same high-quality service you expect.</p>
                    <p>All other details of your booking remain the same.</p>
                    <p>If you have any questions or concerns, please contact us.</p>
                    <p>Best regards,<br>Maids of CyFair Team</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"Hi {customer_name}, Your cleaner for {booking_details.get('booking_date', 'TBD')} has been changed from {old_cleaner} to {new_cleaner}."
        
        return self.send_email(customer_email, subject, html_content, text_content)

# Global instance
email_service = EmailService()
