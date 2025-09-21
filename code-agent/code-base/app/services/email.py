"""
Email service for notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from app.core.config import settings


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email to single recipient"""
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            print("SMTP configuration not available")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_bulk_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> int:
        """Send email to multiple recipients"""
        success_count = 0
        for email in to_emails:
            if self.send_email(email, subject, body, html_body):
                success_count += 1
        return success_count
    
    def send_order_confirmation(self, user_email: str, order_number: str) -> bool:
        """Send order confirmation email"""
        subject = f"Order Confirmation - {order_number}"
        body = f"""
        Thank you for your order!
        
        Order Number: {order_number}
        
        We have received your order and will process it shortly.
        
        Best regards,
        E-commerce Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Order Confirmation</h2>
            <p>Thank you for your order!</p>
            <p><strong>Order Number:</strong> {order_number}</p>
            <p>We have received your order and will process it shortly.</p>
            <p>Best regards,<br>E-commerce Team</p>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)
    
    def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request"
        reset_url = f"https://yourapp.com/reset-password?token={reset_token}"
        
        body = f"""
        Password Reset Request
        
        You requested a password reset for your account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        E-commerce Team
        """
        
        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your account.</p>
            <p><a href="{reset_url}">Click here to reset your password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>E-commerce Team</p>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, body, html_body)


# Global email service instance
email_service = EmailService()
