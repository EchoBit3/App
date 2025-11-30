from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import html
class TareaRequest(BaseModel):
    """Modelo para el request de análisis de tarea"""
    texto: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Texto de la tarea o instrucción a analizar"
    )
    @field_validator('texto')
    @classmethod
    def validar_texto(cls, v: str) -> str:
        """Valida y sanitiza el texto contra inyecciones"""
        if not v or not v.strip():
            raise ValueError('El texto no puede estar vacío')
        # Sanitizar: eliminar caracteres de control
        texto_limpio = ''.join(char for char in v if ord(char) >= 32 or char in '\n\r\t')
        # Escape HTML para prevenir XSS
        texto_limpio = html.escape(texto_limpio.strip())
        # Validar que no contenga solo caracteres especiales
        if not re.search(r'[a-zA-Z0-9]', texto_limpio):
            raise ValueError('El texto debe contener al menos caracteres alfanuméricos')
        # Validar longitud después de sanitización
        if len(texto_limpio) < 10:
            raise ValueError('El texto debe tener al menos 10 caracteres válidos')
        return texto_limpio
    class Config:
        json_schema_extra = {
            "example": {
                "texto": "Hacer un análisis del mercado para el viernes"
            }
        }
class TareaResponse(BaseModel):
    """Modelo para la respuesta del análisis"""
    pasos: List[str] = Field(..., description="Lista de pasos concretos y accionables")
    ambiguedades: List[str] = Field(..., description="Información faltante o poco clara")
    preguntas_sugeridas: List[str] = Field(..., description="Preguntas para clarificar")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadatos adicionales del análisis"
    )
    class Config:
        json_schema_extra = {
            "example": {
                "pasos": [
                    "Definir qué tipo de mercado analizar",
                    "Investigar competidores principales",
                    "Recopilar datos de mercado actuales"
                ],
                "ambiguedades": [
                    "No se especifica el tipo de mercado",
                    "Falta el formato de entrega",
                    "No hay extensión definida"
                ],
                "preguntas_sugeridas": [
                    "¿Qué mercado específico debo analizar?",
                    "¿En qué formato debe entregarse?",
                    "¿Cuántas páginas o slides debe tener?"
                ],
                "metadata": {
                    "total_pasos": 3,
                    "total_ambiguedades": 3,
                    "total_preguntas": 3,
                    "timestamp": "2025-11-29T10:30:00"
                }
            }
        }
class ErrorResponse(BaseModel):
    """Modelo para respuestas de error"""
    error: str = Field(..., description="Mensaje de error")
    detail: Optional[str] = Field(None, description="Detalles adicionales del error")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Servicio de IA no disponible",
                "detail": "Verifica la configuración de GEMINI_API_KEY",
                "timestamp": "2025-11-29T10:30:00"
            }
        }
class HealthResponse(BaseModel):
    """Modelo para respuesta de health check"""
    status: str = Field(..., description="Estado del servicio")
    ai_service: str = Field(..., description="Estado del servicio de IA")
    version: str = Field(..., description="Versión de la API")
    uptime: Optional[float] = Field(None, description="Tiempo activo en segundos")
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "ai_service": "ready",
                "version": "1.0.0",
                "uptime": 3600.5
            }
        }
class EjemploItem(BaseModel):
    """Modelo para un ejemplo individual"""
    categoria: str = Field(..., description="Categoría del ejemplo")
    texto: str = Field(..., description="Texto del ejemplo")
class EjemplosResponse(BaseModel):
    """Modelo para respuesta de ejemplos"""
    ejemplos: List[EjemploItem] = Field(..., description="Lista de ejemplos")
    total: int = Field(..., description="Total de ejemplos disponibles")
class StatsResponse(BaseModel):
    """Modelo para estadísticas de la API"""
    total_requests: int = Field(..., description="Total de requests procesados")
    successful_requests: int = Field(..., description="Requests exitosos")
    failed_requests: int = Field(..., description="Requests fallidos")
    average_response_time: float = Field(..., description="Tiempo promedio de respuesta (ms)")
    uptime: float = Field(..., description="Tiempo activo (segundos)")