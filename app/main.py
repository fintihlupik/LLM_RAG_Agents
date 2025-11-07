"""
Punto de entrada principal del asistente financiero.
API REST con FastAPI.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import setup_logger, get_logger
from app.core.llm.client import groq_client
from app.api.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.api.routes import health_router, documents_router

# Configurar logger principal
setup_logger("app", level=20)  # 20 = INFO
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Startup y shutdown hooks.
    """
    # STARTUP
    logger.info("=== Iniciando Asistente Financiero ===")
    logger.info(f"Configuración: Modelo={settings.llm_model}, Temp={settings.temperature}")
    
    # Verificar conexión con Groq
    if groq_client.test_connection():
        logger.info("✓ Conexión con Groq verificada")
    else:
        logger.warning("⚠ No se pudo verificar la conexión con Groq")
    
    logger.info("✓ API lista para recibir peticiones")
    
    yield  # App funcionando
    
    # SHUTDOWN
    logger.info("Cerrando aplicación...")


# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para análisis de informes financieros usando LLM + RAG + Agentes",
    lifespan=lifespan
)

# Registrar middlewares (orden importa: se ejecutan de arriba a abajo)
app.add_middleware(ErrorHandlingMiddleware)  # Primero: captura errores
app.add_middleware(LoggingMiddleware)  # Segundo: loguea requests

# CORS (permite peticiones desde navegadores)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(health_router)
app.include_router(documents_router)


# Para ejecutar directamente con python (desarrollo)
if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor de desarrollo...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Recarga automática al cambiar código
    )
