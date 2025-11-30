from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
import os
# Importar utilidades de encriptación
from encryption import encrypt_data, decrypt_data, encrypt_email, decrypt_email
# Base para modelos
Base = declarative_base()
class Usuario(Base):
    """Modelo de usuario con encriptación de datos sensibles"""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    _email = Column("email", String(500), unique=True, nullable=False, index=True)  # Encriptado
    hashed_password = Column(String(255), nullable=False)  # Ya es hash, no se encripta
    _nombre_completo = Column("nombre_completo", String(500))  # Encriptado
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    # OAuth fields
    oauth_provider = Column(String(50))  # 'google', 'github', etc.
    oauth_id = Column(String(255))  # ID del proveedor OAuth
    email_verified = Column(Boolean, default=False)
    # Email verification fields
    verification_token = Column(String(255))
    verification_token_expires = Column(DateTime)
    # Relación con consultas
    consultas = relationship("Consulta", back_populates="usuario", cascade="all, delete-orphan")
    # Propiedades híbridas para encriptación automática
    @hybrid_property
    def email(self):
        """Desencripta email al leer"""
        return decrypt_email(self._email) if self._email else None
    @email.setter
    def email(self, value):
        """Encripta email al guardar"""
        self._email = encrypt_email(value) if value else None
    @hybrid_property
    def nombre_completo(self):
        """Desencripta nombre al leer"""
        return decrypt_data(self._nombre_completo) if self._nombre_completo else None
    @nombre_completo.setter
    def nombre_completo(self, value):
        """Encripta nombre al guardar"""
        self._nombre_completo = encrypt_data(value) if value else None
    def __repr__(self):
        return f"<Usuario {self.username}>"
class Consulta(Base):
    """Modelo de consulta/análisis con encriptación de texto sensible"""
    __tablename__ = "consultas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    _texto_original = Column("texto_original", Text, nullable=False)  # Encriptado
    pasos = Column(Text)  # JSON string (resultado IA, no tan sensible)
    ambiguedades = Column(Text)  # JSON string
    preguntas = Column(Text)  # JSON string
    tiempo_respuesta_ms = Column(Integer)  # Tiempo de procesamiento
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now, index=True)
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="consultas")
    # Propiedad híbrida para texto_original
    @hybrid_property
    def texto_original(self):
        """Desencripta texto al leer"""
        return decrypt_data(self._texto_original) if self._texto_original else None
    @texto_original.setter
    def texto_original(self, value):
        """Encripta texto al guardar"""
        self._texto_original = encrypt_data(value) if value else None
    def __repr__(self):
        return f"<Consulta {self.id} - Usuario {self.usuario_id}>"
# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demystify.db")
# Crear engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Cambiar a True para debug SQL
)
# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("Base de datos inicializada")
def get_db():
    """
    Dependency para obtener sesión de BD
    Usar con FastAPI Depends
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def reset_db():
    """
    CUIDADO: Elimina y recrea todas las tablas
    Solo usar en desarrollo
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Base de datos reseteada")
if __name__ == "__main__":
    # Test: crear tablas
    init_db()
    # Test: crear sesión
    db = SessionLocal()
    # Verificar tablas
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n Tablas creadas: {tables}")
    db.close()