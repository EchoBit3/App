import logging
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import traceback
class StructuredLogger:
    def __init__(self, name: str, log_file: Optional[str] = "api.log", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.handlers.clear()  # Limpiar handlers existentes
        # Formatter estructurado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Console handler (desarrollo)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        # File handler (producción)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    def _build_context(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
        }
        if extra:
            context.update(extra)
        return context
    def info(self, message: str, **kwargs):
        context = self._build_context(message, kwargs)
        self.logger.info(json.dumps(context) if kwargs else message)
    def warning(self, message: str, **kwargs):
        context = self._build_context(message, kwargs)
        self.logger.warning(json.dumps(context) if kwargs else message)
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        context = self._build_context(message, kwargs)
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
            context["stack_trace"] = traceback.format_exc()
        self.logger.error(json.dumps(context) if (kwargs or error) else message)
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        context = self._build_context(message, kwargs)
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
            context["stack_trace"] = traceback.format_exc()
        self.logger.critical(json.dumps(context) if (kwargs or error) else message)
    def debug(self, message: str, **kwargs):
        context = self._build_context(message, kwargs)
        self.logger.debug(json.dumps(context) if kwargs else message)
class RequestLogger:
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    def log_request(self, method: str, path: str, user_id: Optional[int] = None, **kwargs):
        self.logger.info(
            f"{method} {path}",
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )
    def log_response(self, method: str, path: str, status_code: int,
                     response_time_ms: float, **kwargs):
        level = "info" if status_code < 400 else "warning"
        log_func = getattr(self.logger, level)
        log_func(
            f"{method} {path} - {status_code} ({response_time_ms:.2f}ms)",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            **kwargs
        )
    def log_error(self, method: str, path: str, error: Exception, **kwargs):
        self.logger.error(
            f"Error en {method} {path}",
            error=error,
            method=method,
            path=path,
            **kwargs
        )
class BusinessLogger:
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    def log_user_action(self, action: str, user_id: int, **kwargs):
        self.logger.info(
            f"User action: {action}",
            action=action,
            user_id=user_id,
            **kwargs
        )
    def log_ai_call(self, input_length: int, response_time_ms: float,
                    success: bool, **kwargs):
        self.logger.info(
            (
                f"AI call - Input: {input_length} chars, "
                f"Time: {response_time_ms:.0f}ms, Success: {success}"
            ),
            input_length=input_length,
            response_time_ms=response_time_ms,
            success=success,
            **kwargs
        )
    def log_cache_hit(self, cache_key: str):
        self.logger.debug(
            f"Cache HIT: {cache_key[:50]}...",
            cache_key=cache_key,
            cache_hit=True
        )
    def log_cache_miss(self, cache_key: str):
        self.logger.debug(
            f"Cache MISS: {cache_key[:50]}...",
            cache_key=cache_key,
            cache_hit=False
        )
# Singleton loggers
_main_logger: Optional[StructuredLogger] = None
_request_logger: Optional[RequestLogger] = None
_business_logger: Optional[BusinessLogger] = None
def get_logger() -> StructuredLogger:
    global _main_logger
    if _main_logger is None:
        _main_logger = StructuredLogger("demystify", log_file="logs/api.log")
    return _main_logger
def get_request_logger() -> RequestLogger:
    global _request_logger
    if _request_logger is None:
        _request_logger = RequestLogger(get_logger())
    return _request_logger
def get_business_logger() -> BusinessLogger:
    global _business_logger
    if _business_logger is None:
        _business_logger = BusinessLogger(get_logger())
    return _business_logger
# Para compatibilidad con código existente
def setup_logging(level=logging.INFO):
    global _main_logger
    _main_logger = StructuredLogger("demystify", log_file="logs/api.log", level=level)
    return _main_logger