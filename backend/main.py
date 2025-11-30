from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import EmailStr
import sys
from pathlib import Path
from time import time
import logging
import json
# Sistema de logging centralizado
from logger import get_logger, get_request_logger, get_business_logger
# Imports locales
from models import (
    TareaRequest, TareaResponse, ErrorResponse,
    HealthResponse, EjemplosResponse, EjemploItem, StatsResponse
)
from middleware import (
    RequestLoggingMiddleware, RequestStatsMiddleware, StatsTracker,
    RateLimitMiddleware, APIKeyMiddleware, SecurityHeadersMiddleware
)
from config import get_settings
from utils import SimpleCache, generate_cache_key, measure_time
# Database y Auth
from database import get_db, init_db, Usuario, Consulta
from auth import (
    get_current_user, get_current_admin,
    UserCreate, UserLogin, UserResponse, Token,
    create_user, login_user
)
# OAuth y Rate Limiting
from oauth import google_login, google_callback, is_oauth_enabled, OAUTH_ENABLED
from rate_limiter import setup_rate_limiting, limiter, RATE_LIMITS
# Agregar el directorio raíz al path para importar shared
sys.path.append(str(Path(__file__).parent.parent))
from shared.ai_service import AIService
# Configurar logging estructurado
logger = get_logger()
request_logger = get_request_logger()
business_logger = get_business_logger()
# Obtener configuración
settings = get_settings()
# Inicializar trackers y cache
stats_tracker = StatsTracker()
cache = SimpleCache(ttl=settings.cache_ttl)
start_time = time()
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(
        "Iniciando De-Mystify API",
        version=settings.app_version,
        host=settings.host,
        port=settings.port
    )
    # Inicializar base de datos
    init_db()
    logger.info("Base de datos inicializada")
    # Configurar rate limiting
    setup_rate_limiting(app)
    logger.info("Rate limiting configurado")
    yield
    # Shutdown
    logger.info("Cerrando De-Mystify API")
    logger.info(f"Stats finales: {stats_tracker.get_stats()}")
# Crear app FastAPI
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)
# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
# Agregar middlewares de seguridad (en orden de ejecución)
if settings.enable_security_headers:
    app.add_middleware(SecurityHeadersMiddleware)
if settings.enable_rate_limit:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_window=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window
    )
if settings.require_api_key:
    api_keys = settings.get_api_keys_list()
    if api_keys:
        app.add_middleware(
            APIKeyMiddleware,
            api_keys=api_keys,
            enabled=True
        )
        logger.info(f"API Key authentication enabled ({len(api_keys)} keys)")
    else:
        logger.warning("ADVERTENCIA: require_api_key=True but no API keys configured")
# Agregar middlewares personalizados
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestStatsMiddleware, stats_tracker=stats_tracker)
# Inicializar servicio de IA (singleton)
ai_service = None
try:
    ai_service = AIService()
    logger.info("Servicio de IA inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar servicio de IA: {str(e)}")
# ==================== ENDPOINTS ====================
@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "De-Mystify API está funcionando",
        "version": settings.app_version,
        "docs": "/docs",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/desambiguar",
            "examples": "/api/ejemplos",
            "stats": "/api/stats"
        }
    }
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    uptime = time() - start_time
    return HealthResponse(
        status="healthy" if ai_service else "degraded",
        ai_service="ready" if ai_service else "not initialized",
        version=settings.app_version,
        uptime=round(uptime, 2)
    )
# ==================== AUTENTICACIÓN ====================
@app.post("/api/auth/register", response_model=Token, tags=["Autenticación"])
@limiter.limit(RATE_LIMITS["auth_register"])
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Crear usuario
        user = create_user(db, user_data)
        # Login automático
        login_data = UserLogin(username=user.username, password=user_data.password)
        token = login_user(db, login_data)
        business_logger.log_user_action(
            "register",
            user.id,
            username=user.username,
            email=user.email
        )
        return token
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en registro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )
@app.post("/api/auth/login", response_model=Token, tags=["Autenticación"])
@limiter.limit(RATE_LIMITS["auth_login"])
async def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        token = login_user(db, login_data)
        business_logger.log_user_action(
            "login",
            token.user["id"],
            username=login_data.username
        )
        return token
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar sesión: {str(e)}"
        )
@app.get("/api/auth/me", response_model=UserResponse, tags=["Autenticación"])
async def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user
# ==================== OAUTH (GOOGLE) ====================
@app.get("/api/auth/oauth/status", tags=["OAuth"])
async def oauth_status():
    return {
        "oauth_enabled": OAUTH_ENABLED,
        "providers": ["google"] if OAUTH_ENABLED else []
    }
@app.get("/api/auth/google/login", tags=["OAuth"])
async def auth_google_login(request: Request):
    return await google_login(request)
@app.get("/api/auth/google/callback", response_model=Token, tags=["OAuth"])
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    return await google_callback(request, db)
# ==================== VERIFICACIÓN DE EMAIL ====================
@app.get("/api/auth/verify-email", tags=["Autenticación"])
async def verify_email_endpoint(token: str, db: Session = Depends(get_db)):
    from email_verification import verify_email_token
    usuario = verify_email_token(token, db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    return {
        "success": True,
        "message": "Email verificado correctamente",
        "username": usuario.username
    }
@app.post("/api/auth/resend-verification", tags=["Autenticación"])
@limiter.limit("3 per hour")
async def resend_verification_endpoint(
    request: Request,
    email: EmailStr,
    db: Session = Depends(get_db)
):
    from email_verification import resend_verification_email
    success = resend_verification_email(email, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pudo enviar el email. "
                "Verifica que la cuenta exista y no esté verificada."
            )
        )
    return {
        "success": True,
        "message": "Email de verificación enviado"
    }
# ==================== ANÁLISIS (PROTEGIDO) ====================
@app.post(
    "/api/desambiguar",
    response_model=TareaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Análisis completado exitosamente"},
        400: {"description": "Request inválido", "model": ErrorResponse},
        500: {"description": "Error del servidor", "model": ErrorResponse},
        503: {"description": "Servicio de IA no disponible", "model": ErrorResponse}
    },
    tags=["Análisis"]
)
@measure_time
async def desambiguar_tarea(
    request: TareaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> TareaResponse:
    start_process_time = time()
    # Verificar que el servicio de IA esté disponible
    if not ai_service:
        logger.error("Servicio de IA no inicializado")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "El servicio de IA no está disponible. "
                "Verifica la configuración de GEMINI_API_KEY"
            )
        )
    # Verificar cache si está habilitado
    if settings.enable_cache:
        cache_key = generate_cache_key(request.texto)
        cached_result = cache.get(cache_key)
        if cached_result:
            business_logger.log_cache_hit(cache_key)
            return TareaResponse(**cached_result)
        else:
            business_logger.log_cache_miss(cache_key)
    try:
        logger.info(f"Procesando tarea de {len(request.texto)} caracteres", user_id=current_user.id)
        # Procesar con el servicio de IA con timeout
        import asyncio
        try:
            # Ejecutar con timeout configurado
            resultado = await asyncio.wait_for(
                asyncio.to_thread(ai_service.desambiguar_tarea, request.texto),
                timeout=settings.gemini_timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"Timeout al procesar tarea ({settings.gemini_timeout}s)")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=(
                    f"El análisis tardó más de {settings.gemini_timeout} segundos. "
                    "Intenta con un texto más corto."
                )
            )
        # Verificar si hubo error
        if "error" in resultado:
            logger.error(
                "Error en procesamiento IA",
                error_detail=resultado["error"],
                user_id=current_user.id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=resultado["error"]
            )
        # Agregar metadata
        from datetime import datetime
        tiempo_proceso = (time() - start_process_time) * 1000  # En ms
        # Log de llamada exitosa
        business_logger.log_ai_call(
            input_length=len(request.texto),
            response_time_ms=tiempo_proceso,
            success=True,
            user_id=current_user.id,
            pasos_count=len(resultado.get("pasos", [])),
            ambiguedades_count=len(resultado.get("ambiguedades", []))
        )
        response_data = {
            "pasos": resultado.get("pasos", []),
            "ambiguedades": resultado.get("ambiguedades", []),
            "preguntas_sugeridas": resultado.get("preguntas_sugeridas", []),
            "metadata": {
                "total_pasos": len(resultado.get("pasos", [])),
                "total_ambiguedades": len(resultado.get("ambiguedades", [])),
                "total_preguntas": len(resultado.get("preguntas_sugeridas", [])),
                "timestamp": datetime.now().isoformat(),
                "cached": False
            }
        }
        # Guardar en base de datos
        try:
            consulta = Consulta(
                usuario_id=current_user.id,
                texto_original=request.texto,
                pasos=json.dumps(response_data["pasos"]),
                ambiguedades=json.dumps(response_data["ambiguedades"]),
                preguntas=json.dumps(response_data["preguntas_sugeridas"]),
                tiempo_respuesta_ms=int(tiempo_proceso),
                cached=False
            )
            db.add(consulta)
            # Timeout en commit para evitar bloqueos
            import signal
            def timeout_handler(signum, frame):
                raise TimeoutError("Database commit timeout")
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)  # 5 segundos timeout
            try:
                db.commit()
                logger.info(
                    "Consulta guardada en BD",
                    consulta_id=consulta.id,
                    user_id=current_user.id
                )
            finally:
                signal.alarm(0)  # Cancelar alarma
                signal.signal(signal.SIGALRM, old_handler)
        except TimeoutError:
            logger.error("Timeout al guardar en BD", timeout_seconds=5, user_id=current_user.id)
            db.rollback()
            # No fallar el request si falla el guardado
        except Exception as e:
            logger.error("Error al guardar en BD", error=e, user_id=current_user.id)
            db.rollback()
            # No fallar el request si falla el guardado
        # Guardar en cache
        if settings.enable_cache:
            cache.set(cache_key, response_data)
        logger.info("Tarea procesada exitosamente")
        return TareaResponse(**response_data)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error inesperado al procesar tarea")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )
# ==================== HISTORIAL ====================
@app.get("/api/historial", tags=["Historial"])
async def obtener_historial(
    limit: int = 10,
    offset: int = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Consultar historial del usuario
        consultas = db.query(Consulta)\
            .filter(Consulta.usuario_id == current_user.id)\
            .order_by(Consulta.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        # Total de consultas del usuario
        total = db.query(Consulta).filter(Consulta.usuario_id == current_user.id).count()
        # Formatear respuesta
        historial = []
        for c in consultas:
            historial.append({
                "id": c.id,
                "texto_original": c.texto_original,
                "pasos": json.loads(c.pasos) if c.pasos else [],
                "ambiguedades": json.loads(c.ambiguedades) if c.ambiguedades else [],
                "preguntas": json.loads(c.preguntas) if c.preguntas else [],
                "tiempo_respuesta_ms": c.tiempo_respuesta_ms,
                "cached": c.cached,
                "created_at": c.created_at.isoformat()
            })
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "historial": historial
        }
    except Exception as e:
        logger.error(f"Error al obtener historial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )
@app.get("/api/historial/{consulta_id}", tags=["Historial"])
async def obtener_consulta(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    # Verificar que la consulta pertenezca al usuario
    if consulta.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta consulta"
        )
    return {
        "id": consulta.id,
        "texto_original": consulta.texto_original,
        "pasos": json.loads(consulta.pasos) if consulta.pasos else [],
        "ambiguedades": json.loads(consulta.ambiguedades) if consulta.ambiguedades else [],
        "preguntas": json.loads(consulta.preguntas) if consulta.preguntas else [],
        "tiempo_respuesta_ms": consulta.tiempo_respuesta_ms,
        "cached": consulta.cached,
        "created_at": consulta.created_at.isoformat()
    }
@app.delete("/api/historial/{consulta_id}", tags=["Historial"])
async def eliminar_consulta(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta no encontrada"
        )
    # Verificar que la consulta pertenezca al usuario
    if consulta.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar esta consulta"
        )
    db.delete(consulta)
    db.commit()
    business_logger.log_user_action(
        "delete_query",
        current_user.id,
        consulta_id=consulta_id
    )
    return {"message": "Consulta eliminada exitosamente"}
# ==================== UTILIDADES ====================
@app.get("/api/ejemplos", response_model=EjemplosResponse, tags=["Utilidades"])
async def obtener_ejemplos():
    from shared.config import EJEMPLOS
    ejemplos = [
        EjemploItem(categoria=key, texto=value)
        for key, value in EJEMPLOS.items()
    ]
    return EjemplosResponse(
        ejemplos=ejemplos,
        total=len(ejemplos)
    )
@app.get("/api/stats", response_model=StatsResponse, tags=["Monitoreo"])
async def obtener_estadisticas():
    stats = stats_tracker.get_stats()
    return StatsResponse(**stats)
@app.get("/api/cache/stats", tags=["Monitoreo"])
async def cache_stats():
    return {
        "cache_enabled": settings.enable_cache,
        "cache_size": cache.size(),
        "cache_ttl": settings.cache_ttl
    }
@app.post("/api/cache/clear", tags=["Monitoreo"])
async def clear_cache():
    cache.clear()
    logger.info("Cache limpiado manualmente")
    return {"message": "Cache limpiado correctamente"}
# ==================== EXCEPTION HANDLERS ====================
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail or "Error en la petición",
            detail=str(exc.detail) if exc.detail else None
        ).model_dump()
    )
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Error de validación",
            detail=str(exc)
        ).model_dump()
    )
@app.exception_handler(TimeoutError)
async def timeout_error_handler(request: Request, exc: TimeoutError):
    logger.error(f"⏱️ Timeout error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content=ErrorResponse(
            error="Timeout",
            detail="La operación tardó demasiado tiempo. Intenta nuevamente."
        ).model_dump()
    )
# Manejo de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Error interno del servidor",
            detail=str(exc) if settings.reload else "Ha ocurrido un error inesperado"
        ).model_dump()
    )
if __name__ == "__main__":
    import uvicorn
    logger.info("="*60)
    logger.info("DE-MYSTIFY API")
    logger.info("="*60)
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )