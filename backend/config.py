import os
from functools import lru_cache
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    # API Info
    app_name: str = "De-Mystify API"
    app_version: str = "2.0.0"
    app_description: str = (
        "API REST para convertir instrucciones ambiguas "
        "en tareas concretas usando IA"
    )
    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = True
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]  # Frontend URLs
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST"]
    cors_allow_headers: list = ["*"]
    # Logging
    log_level: str = "INFO"
    log_file: str = "api.log"
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    # Security - API Keys (opcional para proteger endpoints)
    require_api_key: bool = False  # Cambiar a True para activar
    api_keys: str = os.getenv("API_KEYS", "")  # Comma-separated: "key1,key2,key3"
    # Rate Limiting
    enable_rate_limit: bool = True
    rate_limit_requests: int = 60  # Requests por ventana
    rate_limit_window: int = 60  # Segundos (ventana de tiempo)
    rate_limit_by_ip: bool = True
    # Cache
    enable_cache: bool = True
    cache_ttl: int = 300  # 5 minutos
    # Timeouts
    gemini_timeout: int = 30  # Timeout para llamadas a Gemini API (segundos)
    request_timeout: int = 60  # Timeout general de requests
    # Security Headers
    enable_security_headers: bool = True
    def get_api_keys_list(self) -> list:
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]
    class Config:
        env_file = ".env"
        case_sensitive = False
@lru_cache()
@lru_cache()
def get_settings() -> Settings:
    return Settings()