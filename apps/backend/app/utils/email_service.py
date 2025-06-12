"""
Service for sending email messages.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
from typing import Optional
from config.email_settings import email_settings
from config.app_settings import settings

logger = logging.getLogger(__name__)

async def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Sends an email message.

    Args:
        to_email (str): Recipient's email address.
        subject (str): Subject line of the email.
        html_content (str): HTML content of the email.
        text_content (Optional[str], optional): Plain text version of the email. Defaults to None.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    if not email_settings.is_configured:
        logger.warning("SMTP configuration is incomplete. Email cannot be sent.")
        return False
        
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email_settings.EMAIL_FROM
        message["To"] = to_email
        
        # Attach plain text version
        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        
        # Attach HTML version
        message.attach(MIMEText(html_content, "html"))
        
        # Send email via SMTP
        with smtplib.SMTP(email_settings.SMTP_HOST, email_settings.SMTP_PORT) as server:
            server.starttls()
            server.login(email_settings.SMTP_USERNAME, email_settings.SMTP_PASSWORD)
            server.sendmail(email_settings.EMAIL_FROM, to_email, message.as_string())
            
        logger.info(f"Email successfully sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error while sending email: {str(e)}")
        return False

async def send_verification_email(to_email: str, verification_token: str) -> bool:
    """
    Sends a verification email to a user.

    Args:
        to_email (str): Recipient's email address.
        verification_token (str): Unique verification token.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    verification_link = f"{settings.WEBSITE_URL}/auth/verify-email?token={verification_token}"
    
    subject = "Verify your email - FitCoach AI"
    
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to FitCoach AI!</h2>
        <p>Thanks for signing up. Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_link}">Verify my email</a></p>
        <p>Or copy and paste the following link into your browser:</p>
        <p>{verification_link}</p>
        <p>This link will expire in 24 hours.</p>
        <p>If you did not sign up for FitCoach AI, you can ignore this message.</p>
        <p>Best regards,<br>The FitCoach AI Team</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to FitCoach AI!
    
    Thanks for signing up. Please verify your email address by visiting the following link:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you did not sign up for FitCoach AI, you can ignore this message.
    
    Best regards,
    The FitCoach AI Team
    """
    
    return await send_email(to_email, subject, html_content, text_content)

async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Sends a password reset email to a user.

    Args:
        to_email (str): Recipient's email address.
        reset_token (str): Unique reset token.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    reset_link = f"{settings.WEBSITE_URL}/restablecer-password?token={reset_token}"
    
    subject = "Reset your password - FitCoach AI"
    
    html_content = f"""
    <html>
    <body>
        <h2>Forgot your password?</h2>
        <p>We received a request to reset your password. Click the link below to create a new one:</p>
        <p><a href="{reset_link}">Reset my password</a></p>
        <p>Or copy and paste the following link into your browser:</p>
        <p>{reset_link}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you did not request a password reset, you can ignore this message.</p>
        <p>Best regards,<br>The FitCoach AI Team</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Forgot your password?
    
    We received a request to reset your password. Visit the following link to create a new one:
    
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you did not request a password reset, you can ignore this message.
    
    Best regards,
    The FitCoach AI Team
    """
    
    return await send_email(to_email, subject, html_content, text_content)
