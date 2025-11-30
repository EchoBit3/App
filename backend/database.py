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
        return decrypt_email(self._email) if self._email else None
    @email.setter
    def email(self, value):
        self._email = encrypt_email(value) if value else None
    @hybrid_property
    def nombre_completo(self):
        return decrypt_data(self._nombre_completo) if self._nombre_completo else None
    @nombre_completo.setter
    def nombre_completo(self, value):
        self._nombre_completo = encrypt_data(value) if value else None
    def __repr__(self):
        return f"<Usuario {self.username}>"
class Consulta(Base):
    __tablename__ = "consultas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    _texto_original = Column("texto_original", Text, nullable=False)  # Encriptado
    pasos = Column(Text)  # JSON string (resultado IA, no tan sensible)
    ambiguedades = Column(Text)  # JSON string
    preguntas = Column(Text)  # JSON string
    tiempo_respuesta_ms = Column(Integer)  # Tiempo de procesamiento
    cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    usuario = relationship("Usuario", back_populates="consultas")
    @hybrid_property
    def texto_original(self):
        return decrypt_data(self._texto_original) if self._texto_original else None
    @texto_original.setter
    def texto_original(self, value):
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
    Base.metadata.create_all(bind=engine)
    import logging
    logging.info("Base de datos inicializada")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    import logging
    logging.info("Base de datos reseteada")
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