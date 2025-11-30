from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Callable
# Inicializar rate limiter
limiter = Limiter(key_func=get_remote_address)
# Límites configurables
RATE_LIMITS = {
    "auth_login": "5/minute",  # 5 intentos de login por minuto
    "auth_register": "3/hour",  # 3 registros por hora por IP
    "api_general": "100/minute",  # 100 requests generales por minuto
    "api_analizar": "10/minute",  # 10 análisis por minuto
}
def get_rate_limit(endpoint: str) -> str:
    """Obtiene el límite para un endpoint específico"""
    return RATE_LIMITS.get(endpoint, RATE_LIMITS["api_general"])
def setup_rate_limiting(app):
    """
    Configura rate limiting en la aplicación FastAPI
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return limiter