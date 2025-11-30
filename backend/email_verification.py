import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import secrets
from sqlalchemy.orm import Session
from database import Usuario
from config import Settings
settings = Settings()
# Configuración de SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Demystify App")
# URLs del frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Control de verificación
EMAIL_VERIFICATION_REQUIRED = os.getenv("EMAIL_VERIFICATION_REQUIRED", "false").lower() == "true"
EMAIL_VERIFICATION_ENABLED = bool(SMTP_USERNAME and SMTP_PASSWORD)
def generate_verification_token() -> str:
    """
    Genera un token de verificación seguro
    """
    return secrets.token_urlsafe(32)
def is_email_verification_enabled() -> bool:
    """
    Verifica si el sistema de email está configurado
    """
    return EMAIL_VERIFICATION_ENABLED
def send_verification_email(email: str, token: str, username: str) -> bool:
    """
    Envía email de verificación al usuario
    Args:
        email: Email del usuario
        token: Token de verificación
        username: Nombre de usuario
    Returns:
        bool: True si se envió correctamente
    """
    if not EMAIL_VERIFICATION_ENABLED:
        print("ADVERTENCIA: Email verification no configurado (SMTP credentials faltantes)")
        return False
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Verifica tu cuenta - Demystify"
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        msg['To'] = email
        # URL de verificación
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        # Texto plano
        text = f"""
        ¡Hola {username}!
        Gracias por registrarte en Demystify.
        Para verificar tu cuenta, haz clic en el siguiente enlace:
        {verification_url}
        Este enlace expirará en 24 horas.
        Si no creaste esta cuenta, puedes ignorar este email.
        Saludos,
        El equipo de Demystify
        """
        # HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 40px;
                    border-radius: 10px;
                    color: white;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    color: #333;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 28px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin: 20px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #999;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="margin: 0;">🔐 Demystify</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Análisis de Procedimientos con IA</p>
            </div>
            <div class="content">
                <h2>¡Hola {username}! 👋</h2>
                <p>Gracias por registrarte en Demystify.</p>
                <p>Para comenzar a usar tu cuenta, necesitas verificar tu dirección de email:</p>
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verificar mi cuenta</a>
                </div>
                <p style="font-size: 14px; color: #666;">
                    O copia y pega este enlace en tu navegador:<br>
                    <code style=(
                        "background: #f5f5f5; padding: 8px; "
                        "display: block; margin-top: 10px; word-break: break-all;"
                    )>
                        {verification_url}
                    </code>
                </p>
                <p style="font-size: 13px; color: #999; margin-top: 30px;">
                    ⏱️ Este enlace expirará en 24 horas.<br>
                    Si no creaste esta cuenta, puedes ignorar este email.
                </p>
            </div>
            <div class="footer">
                <p>© 2025 Demystify - Sistema de análisis de procedimientos</p>
            </div>
        </body>
        </html>
        """
        # Agregar ambas versiones
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        # Enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Email de verificación enviado a {email}")
        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False
def verify_email_token(token: str, db: Session) -> Optional[Usuario]:
    """
    Verifica un token de email y marca la cuenta como verificada
    Args:
        token: Token de verificación
        db: Sesión de base de datos
    Returns:
        Usuario si el token es válido, None si no
    """
    try:
        # Buscar usuario con este token
        usuario = db.query(Usuario).filter(
            Usuario.verification_token == token
        ).first()
        if not usuario:
            print("Token no encontrado")
            return None
        # Verificar si ya está verificado
        if usuario.email_verified:
            print("Email ya verificado anteriormente")
            return usuario
        # Verificar expiración (24 horas)
        if usuario.verification_token_expires:
            if datetime.utcnow() > usuario.verification_token_expires:
                print("Token expirado")
                return None
        # Marcar como verificado
        usuario.email_verified = True
        usuario.verification_token = None
        usuario.verification_token_expires = None
        db.commit()
        print(f"Email verificado para usuario {usuario.username}")
        return usuario
    except Exception as e:
        print(f"Error verificando token: {str(e)}")
        db.rollback()
        return None
def resend_verification_email(email: str, db: Session) -> bool:
    """
    Reenvía email de verificación
    Args:
        email: Email del usuario
        db: Sesión de base de datos
    Returns:
        bool: True si se envió correctamente
    """
    try:
        # Buscar usuario
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            return False
        if usuario.email_verified:
            print("Email ya está verificado")
            return False
        # Generar nuevo token
        token = generate_verification_token()
        usuario.verification_token = token
        usuario.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        # Enviar email
        return send_verification_email(usuario.email, token, usuario.username)
    except Exception as e:
        print(f"Error reenviando email: {str(e)}")
        db.rollback()
        return False
def should_verify_email() -> bool:
    """
    Determina si se debe requerir verificación de email
    """
    return EMAIL_VERIFICATION_REQUIRED and EMAIL_VERIFICATION_ENABLED