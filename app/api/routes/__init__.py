"""
Archivo de inicialización del paquete routes.
Importa y expone todos los routers.
"""
from app.api.routes.health import router as health_router
from app.api.routes.documents import router as documents_router

# Lista de todos los routers para registrar en main.py
__all__ = ["health_router", "documents_router"]
