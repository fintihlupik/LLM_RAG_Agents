"""
Rutas de health check y estado del sistema.
"""
from datetime import datetime
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/")
async def root():
    """
    Endpoint raíz - información básica de la API.
    """
    return {
        "nombre": settings.app_name,
        "version": settings.app_version,
        "estado": "operativo",
        "documentacion": "/docs"
    }


@router.get("/health")
async def healthcheck():
    """
    Healthcheck - verifica que la API está funcionando.
    
    Útil para:
    - Monitoreo de servicios
    - Docker health checks
    - Load balancers
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modelo_llm": settings.llm_model,
        "version": settings.app_version
    }
