from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
import os
from database import get_db, Usuario
# Configuración
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    import warnings
    SECRET_KEY = "dev-secret-key-CHANGE-IN-PRODUCTION"
    warnings.warn("SECRET_KEY no configurada. Usando clave de desarrollo. NO USAR EN PRODUCCIÓN.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Security scheme
security = HTTPBearer()
# ==================== SCHEMAS ====================
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    nombre_completo: Optional[str] = Field(None, max_length=100)
class UserLogin(BaseModel):
    username: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    nombre_completo: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    class Config:
        from_attributes = True
# ==================== FUNCIONES DE HASHING ====================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
# ==================== JWT ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    from datetime import timezone
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
# ==================== AUTENTICACIÓN ====================
def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return user
def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user
# ==================== FUNCIONES DE USUARIO ====================
def create_user(
    db: Session,
    user_data: UserCreate,
    skip_email_verification: bool = False
) -> Usuario:
    from email_verification import (
        generate_verification_token,
        send_verification_email,
        should_verify_email
    )
    from datetime import timedelta
    # Verificar si el username ya existe
    existing_user = db.query(Usuario).filter(Usuario.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está registrado"
        )
    # Verificar si el email ya existe
    existing_email = db.query(Usuario).filter(Usuario.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    # Generar token de verificación si es necesario
    verification_token = None
    verification_expires = None
    if should_verify_email() and not skip_email_verification:
        verification_token = generate_verification_token()
        verification_expires = datetime.now() + timedelta(hours=24)
    # Crear usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = Usuario(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        nombre_completo=user_data.nombre_completo,
        is_active=True,
        is_admin=False,  # Por defecto no es admin
        verification_token=verification_token,
        verification_token_expires=verification_expires,
        email_verified=skip_email_verification or not should_verify_email()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Enviar email de verificación si corresponde
    if verification_token:
        send_verification_email(db_user.email, verification_token, db_user.username)
    return db_user
def login_user(db: Session, login_data: UserLogin) -> Token:
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Actualizar último login
    from datetime import timezone
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    # Crear token
    access_token = create_access_token(data={"sub": user.id})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nombre_completo": user.nombre_completo,
            "is_admin": user.is_admin
        }
    )
if __name__ == "__main__":
    # Test de hashing
    password = "mi_password_123"
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print(f"Verify: {verify_password(password, hashed)}")
    # Test de token
    token = create_access_token(data={"sub": 1})
    print(f"\nToken: {token}")
    decoded = decode_access_token(token)
    print(f"Decoded: {decoded}")