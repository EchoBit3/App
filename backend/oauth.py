from authlib.integrations.starlette_client import OAuth
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
import os
from typing import Optional
from database import Usuario
from auth import create_access_token, get_password_hash
from datetime import timedelta
# Configuración OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
# Inicializar OAuth
oauth = OAuth()
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    OAUTH_ENABLED = True
else:
    OAUTH_ENABLED = False
    import warnings
    warnings.warn(
        "Google OAuth no configurado. Define GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET "
        "en variables de entorno para habilitar login con Google."
    )
async def google_login(request: Request):
    if not OAUTH_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="OAuth no está configurado. Contacta al administrador."
        )
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)
async def google_callback(request: Request, db: Session):
    if not OAUTH_ENABLED:
        raise HTTPException(
            status_code=501,
            detail="OAuth no está configurado."
        )
    try:
        # Obtener token de Google
        token = await oauth.google.authorize_access_token(request)
        # Obtener información del usuario
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=400,
                detail="No se pudo obtener información del usuario"
            )
        email = user_info.get('email')
        name = user_info.get('name')
        google_id = user_info.get('sub')  # Google user ID
        if not email:
            raise HTTPException(status_code=400, detail="Email no proporcionado por Google")
        # Buscar usuario existente
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario:
            # Usuario existe - actualizar última sesión
            if not usuario.is_active:
                raise HTTPException(status_code=403, detail="Cuenta desactivada")
        else:
            # Crear nuevo usuario
            username = email.split('@')[0]  # Usar parte del email como username
            # Verificar si username ya existe
            count = db.query(Usuario).filter(Usuario.username.like(f"{username}%")).count()
            if count > 0:
                username = f"{username}{count + 1}"
            usuario = Usuario(
                username=username,
                email=email,
                nombre_completo=name,
                password_hash=get_password_hash(google_id),  # Hash del Google ID como password
                is_active=True,
                oauth_provider="google",
                oauth_id=google_id
            )
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        # Crear token JWT
        access_token = create_access_token(
            data={"sub": usuario.username, "user_id": usuario.id},
            expires_delta=timedelta(days=7)
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": usuario.id,
                "username": usuario.username,
                "email": usuario.email,
                "nombre_completo": usuario.nombre_completo,
                "is_active": usuario.is_active,
                "is_admin": usuario.is_admin,
                "created_at": usuario.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en autenticación con Google: {str(e)}"
        )
def is_oauth_enabled() -> bool:
    return OAUTH_ENABLED