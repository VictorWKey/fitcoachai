import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Configuración del servidor SMTP
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
WEBSITE_URL = os.getenv("WEBSITE_URL")

async def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """
    Envía un correo electrónico
    
    Args:
        to_email: Dirección de correo del destinatario
        subject: Asunto del correo
        html_content: Contenido HTML del correo
        text_content: Contenido de texto plano (opcional)
    
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
        logger.warning("Configuración SMTP incompleta. No se puede enviar el correo.")
        return False
        
    try:
        # Crear mensaje
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message["To"] = to_email
        
        # Versión texto plano
        if text_content:
            message.attach(MIMEText(text_content, "plain"))
        
        # Versión HTML
        message.attach(MIMEText(html_content, "html"))
        
        # Enviar email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, message.as_string())
            
        logger.info(f"Email enviado correctamente a {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email: {str(e)}")
        return False

async def send_verification_email(to_email: str, verification_token: str) -> bool:
    """
    Envía un correo de verificación
    
    Args:
        to_email: Email del usuario
        verification_token: Token único de verificación
    
    Returns:
        bool: True si se envió correctamente
    """
    verification_link = f"{WEBSITE_URL}/auth/verify-email?token={verification_token}"
    
    subject = "Verifica tu email - FitCoach AI"
    
    html_content = f"""
    <html>
    <body>
        <h2>¡Bienvenido a FitCoach AI!</h2>
        <p>Gracias por registrarte. Por favor verifica tu dirección de correo electrónico haciendo clic en el enlace a continuación:</p>
        <p><a href="{verification_link}">Verificar mi email</a></p>
        <p>O copia y pega el siguiente enlace en tu navegador:</p>
        <p>{verification_link}</p>
        <p>Este enlace expirará en 24 horas.</p>
        <p>Si no te has registrado en FitCoach AI, puedes ignorar este mensaje.</p>
        <p>Saludos,<br>El equipo de FitCoach AI</p>
    </body>
    </html>
    """
    
    text_content = f"""
    ¡Bienvenido a FitCoach AI!
    
    Gracias por registrarte. Por favor verifica tu dirección de correo electrónico visitando el siguiente enlace:
    
    {verification_link}
    
    Este enlace expirará en 24 horas.
    
    Si no te has registrado en FitCoach AI, puedes ignorar este mensaje.
    
    Saludos,
    El equipo de FitCoach AI
    """
    
    return await send_email(to_email, subject, html_content, text_content)

async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Envía un correo de restablecimiento de contraseña
    
    Args:
        to_email: Email del usuario
        reset_token: Token único de restablecimiento
    
    Returns:
        bool: True si se envió correctamente
    """
    reset_link = f"{WEBSITE_URL}/restablecer-password?token={reset_token}"
    
    subject = "Restablecer contraseña - FitCoach AI"
    
    html_content = f"""
    <html>
    <body>
        <h2>¿Olvidaste tu contraseña?</h2>
        <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
        <p><a href="{reset_link}">Restablecer mi contraseña</a></p>
        <p>O copia y pega el siguiente enlace en tu navegador:</p>
        <p>{reset_link}</p>
        <p>Este enlace expirará en 1 hora.</p>
        <p>Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje.</p>
        <p>Saludos,<br>El equipo de FitCoach AI</p>
    </body>
    </html>
    """
    
    text_content = f"""
    ¿Olvidaste tu contraseña?
    
    Hemos recibido una solicitud para restablecer tu contraseña. Visita el siguiente enlace para crear una nueva contraseña:
    
    {reset_link}
    
    Este enlace expirará en 1 hora.
    
    Si no solicitaste restablecer tu contraseña, puedes ignorar este mensaje.
    
    Saludos,
    El equipo de FitCoach AI
    """
    
    return await send_email(to_email, subject, html_content, text_content) 