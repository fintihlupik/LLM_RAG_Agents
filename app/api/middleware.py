"""
Middlewares de la aplicación.
Procesan todas las requests/responses de forma global.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware #Es una clase base que ofrece una estructura estándar para crear tus propios middlewares asíncronos. La heredo y sobreescribo su método dispatch()

from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para loguear todas las peticiones HTTP.
    Registra: método, path, duración, status code.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa cada request y response.
        
        Args:
            request: Request entrante
            call_next: Siguiente middleware/endpoint
        
        Returns:
            Response procesada
        """
        # Inicio del request
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"→ {method} {path}")
        
        # Ejecutar el endpoint
        response = await call_next(request)
        
        # Calcular duración
        duration = time.time() - start_time
        status_code = response.status_code
        
        # Log del resultado
        logger.info(f"← {method} {path} - {status_code} ({duration:.3f}s)")
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para manejar errores no capturados.
    Evita que la app crashee y devuelve errores formateados.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Captura excepciones no manejadas.
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error no capturado: {str(e)}", exc_info=True)
            # Aquí podrías devolver una respuesta JSON personalizada
            # Por ahora, re-lanzamos para que FastAPI lo maneje
            raise
