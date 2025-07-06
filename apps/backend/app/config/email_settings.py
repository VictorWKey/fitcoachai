"""
Email service configuration for FitCoach AI.

Handles SMTP server settings for sending verification emails
and password reset notifications.
"""

import os

class EmailSettings:
    """Configuration for the email service."""
    
    # SMTP server configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@fitcoachai.com")
    
    # Verification that the configuration is valid
    @property
    def is_configured(self) -> bool:
        """Checks if the email service is correctly configured."""
        return all([self.SMTP_HOST, self.SMTP_PORT, self.SMTP_USERNAME, self.SMTP_PASSWORD])

email_settings = EmailSettings()
