"""
Email service for sending OTP and notification emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


class EmailService:
    """Email service using SMTP for sending emails."""
    
    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (optional)
            
        Returns:
            True if email sent successfully
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{Config.EMAIL_FROM_NAME} <{Config.EMAIL_USERNAME}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server
            with smtplib.SMTP(Config.EMAIL_SMTP_HOST, Config.EMAIL_SMTP_PORT) as server:
                server.starttls()
                server.login(Config.EMAIL_USERNAME, Config.EMAIL_PASSWORD)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_otp(to_email: str, otp_code: str, name: str = None) -> bool:
        """
        Send OTP verification email.
        
        Args:
            to_email: Recipient email
            otp_code: The OTP code
            name: User's name (optional)
            
        Returns:
            True if sent successfully
        """
        greeting = f"Hi {name}," if name else "Hi,"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #4F46E5; letter-spacing: 4px; text-align: center; padding: 20px; background: white; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>InfoVault</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>Your verification code is:</p>
                    <div class="otp-code">{otp_code}</div>
                    <p>This code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; InfoVault. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {greeting}
        
        Your InfoVault verification code is: {otp_code}
        
        This code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.
        
        If you didn't request this code, please ignore this email.
        """
        
        return EmailService.send_email(
            to_email=to_email,
            subject=f"Your InfoVault Verification Code: {otp_code}",
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_expiry_reminder(
        to_email: str,
        document_name: str,
        expiry_date: str,
        days_until_expiry: int,
        name: str = None
    ) -> bool:
        """
        Send document expiry reminder email.
        
        Args:
            to_email: Recipient email
            document_name: Name of the expiring document
            expiry_date: Formatted expiry date
            days_until_expiry: Days until expiry
            name: User's name (optional)
            
        Returns:
            True if sent successfully
        """
        greeting = f"Hi {name}," if name else "Hi,"
        
        urgency = "URGENT: " if days_until_expiry <= 1 else ""
        urgency_color = "#EF4444" if days_until_expiry <= 1 else "#F59E0B"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {urgency_color}; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .document-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {urgency_color}; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Document Expiry Reminder</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>This is a reminder that one of your documents is expiring soon:</p>
                    <div class="document-info">
                        <p><strong>Document:</strong> {document_name}</p>
                        <p><strong>Expires:</strong> {expiry_date}</p>
                        <p><strong>Days Remaining:</strong> {days_until_expiry} day(s)</p>
                    </div>
                    <p>Please take appropriate action to renew or update this document.</p>
                </div>
                <div class="footer">
                    <p>&copy; InfoVault. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        {greeting}
        
        This is a reminder that one of your documents is expiring soon:
        
        Document: {document_name}
        Expires: {expiry_date}
        Days Remaining: {days_until_expiry} day(s)
        
        Please take appropriate action to renew or update this document.
        """
        
        return EmailService.send_email(
            to_email=to_email,
            subject=f"{urgency}Document Expiry Reminder: {document_name}",
            html_content=html_content,
            text_content=text_content
        )
    
    @staticmethod
    def send_password_changed(to_email: str, name: str = None) -> bool:
        """
        Send password change notification.
        
        Args:
            to_email: Recipient email
            name: User's name (optional)
            
        Returns:
            True if sent successfully
        """
        greeting = f"Hi {name}," if name else "Hi,"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .alert {{ background: #FEF3C7; border: 1px solid #F59E0B; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Changed</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>Your InfoVault password was recently changed.</p>
                    <div class="alert">
                        <p><strong>⚠️ If you did not make this change:</strong></p>
                        <p>Please contact our support team immediately to secure your account.</p>
                    </div>
                    <p>If you made this change, no further action is needed.</p>
                </div>
                <div class="footer">
                    <p>&copy; InfoVault. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            to_email=to_email,
            subject="Your InfoVault Password Was Changed",
            html_content=html_content
        )
