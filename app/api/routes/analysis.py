"""
Rutas para análisis con LLM.
Endpoints para resumir y analizar documentos.

Principio: Thin Controllers - Solo maneja HTTP, delega lógica a services.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from app.services.analysis_service import analysis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class SummarizeRequest(BaseModel):
    """Modelo para la petición de resumen."""
    filename: str


class SummarizeResponse(BaseModel):
    """Modelo para la respuesta de resumen."""
    filename: str
    original_length: int
    summary: str
    summary_length: int
    model_used: str


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Resume un documento PDF usando LLM (sin RAG).
    
    Este endpoint solo maneja la capa HTTP:
    - Recibe la request
    - Valida el input (hecho por Pydantic)
    - Delega al servicio
    - Devuelve la response
    
    Args:
        request.filename: Nombre del archivo en uploads/raw
    
    Returns:
        Resumen del documento con estadísticas
    """
    logger.info(f"Request recibida: resumir {request.filename}")
    
    # Delegar toda la lógica al servicio
    result = await analysis_service.summarize_document(request.filename)
    
    return SummarizeResponse(**result)
