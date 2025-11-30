from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock
import logging
logger = logging.getLogger(__name__)
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        process_time = (time() - start_time) * 1000
        logger.info(
            f"{request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.2f}ms"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response
class RequestStatsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, stats_tracker):
        super().__init__(app)
        self.stats = stats_tracker
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        try:
            response = await call_next(request)
            process_time = (time() - start_time) * 1000
            self.stats.record_request(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                response_time=process_time
            )
            return response
        except Exception as e:
            self.stats.record_error()
            raise
class StatsTracker:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.start_time = time()
    def record_request(self, path: str, method: str, status_code: int, response_time: float):
        self.total_requests += 1
        if 200 <= status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        self.response_times.append(response_time)
        # Mantener solo los últimos 1000 tiempos
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    def record_error(self):
        self.total_requests += 1
        self.failed_requests += 1
    def get_stats(self) -> dict:
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        uptime = time() - self.start_time
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time": round(avg_time, 2),
            "uptime": round(uptime, 2)
        }
    def reset(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.start_time = time()
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_window: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}
        self.lock = Lock()  # Thread safety para acceso concurrente
        self.max_ips_tracked = 10000  # Prevenir memory leak
    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    def _clean_old_requests(self, ip: str):
        with self.lock:
            cutoff_time = datetime.now() - timedelta(seconds=self.window_seconds)
            self.requests[ip] = [
                req_time for req_time in self.requests[ip]
                if req_time > cutoff_time
            ]
            # Prevenir memory leak: limpiar IPs inactivas
            if len(self.requests) > self.max_ips_tracked:
                # Eliminar IPs sin requests recientes
                inactive_ips = [ip for ip, times in self.requests.items() if not times]
                for inactive_ip in inactive_ips:
                    del self.requests[inactive_ip]
    async def dispatch(self, request: Request, call_next):
        # Excluir health check y docs de rate limiting
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        client_ip = self._get_client_ip(request)
        self._clean_old_requests(client_ip)
        with self.lock:
            current_requests = len(self.requests[client_ip])
        if current_requests >= self.requests_per_window:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            # Calcular tiempo de espera
            oldest_request = min(self.requests[client_ip])
            expire_time = oldest_request + timedelta(seconds=self.window_seconds)
            retry_after = int((expire_time - datetime.now()).total_seconds())
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": (
                        f"Máximo {self.requests_per_window} requests "
                        f"por {self.window_seconds} segundos"
                    ),
                    "retry_after": max(retry_after, 1)
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                    "Retry-After": str(max(retry_after, 1))
                }
            )
        with self.lock:
            self.requests[client_ip].append(datetime.now())
        response = await call_next(request)
        with self.lock:
            remaining = self.requests_per_window - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(max(remaining, 0))
        response.headers["X-RateLimit-Window"] = str(self.window_seconds)
        return response
class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_keys: list, enabled: bool = True):
        super().__init__(app)
        self.api_keys = set(api_keys)  # Set para búsqueda O(1)
        self.enabled = enabled
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        # Excluir health check y docs de autenticación
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        api_key = (
            request.headers.get("X-API-Key") or
            request.headers.get("Authorization", "").replace("Bearer ", "")
        )
        if not api_key:
            logger.warning(f"Missing API key for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "API key required",
                    "detail": (
                        "Incluye tu API key en el header 'X-API-Key' "
                        "o 'Authorization: Bearer <key>'"
                    )
                },
                headers={"WWW-Authenticate": "ApiKey"}
            )
        if api_key not in self.api_keys:
            logger.warning(f"Invalid API key attempt for {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Invalid API key",
                    "detail": "La API key proporcionada no es válida"
                }
            )
        logger.info(f"Valid API key for {request.url.path}")
        return await call_next(request)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response