from functools import wraps
from time import time
import hashlib
import json
from typing import Optional, Any
import logging
logger = logging.getLogger(__name__)
class SimpleCache:
    """Cache simple en memoria"""
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time() - timestamp < self.ttl:
                logger.debug(f"Cache HIT: {key}")
                return value
            else:
                # Expiró
                del self.cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        logger.debug(f"Cache MISS: {key}")
        return None
    def set(self, key: str, value: Any):
        """Guarda un valor en el cache"""
        self.cache[key] = (value, time())
        logger.debug(f"Cache SET: {key}")
    def clear(self):
        """Limpia todo el cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    def size(self) -> int:
        """Retorna el tamaño del cache"""
        return len(self.cache)
def generate_cache_key(texto: str) -> str:
    """Genera una clave de cache para un texto"""
    return hashlib.md5(texto.encode()).hexdigest()
def measure_time(func):
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        elapsed = (time() - start) * 1000
        logger.info(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    return wrapper
def format_response(data: dict, success: bool = True) -> dict:
    """Formatea una respuesta estándar"""
    return {
        "success": success,
        "data": data,
        "timestamp": time()
    }
def sanitize_text(text: str, max_length: int = 2000) -> str:
    """Sanitiza y limpia texto de entrada"""
    # Remover espacios extras
    text = " ".join(text.split())
    # Truncar si es muy largo
    if len(text) > max_length:
        text = text[:max_length]
    return text.strip()