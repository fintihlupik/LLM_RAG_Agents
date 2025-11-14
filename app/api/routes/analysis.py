"""
Rutas para análisis con LLM.
Endpoints para resumir y analizar documentos.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.document_service import document_service
from app.core.llm.client import groq_client
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


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Resume un documento PDF usando LLM (sin RAG).
    
    Proceso:
    1. Extrae todo el texto del PDF
    2. Lo envía directo a Groq para resumir
    3. Devuelve el resumen
    
    Args:
        request.filename: Nombre del archivo en uploads/raw
    
    Returns:
        Resumen del documento con estadísticas
    """
    try:
        logger.info(f"Iniciando resumen de: {request.filename}")
        
        # 1. Extraer texto del PDF
        text = document_service.extract_text_from_pdf(request.filename)
        
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="El PDF no contiene texto extraíble"
            )
        
        logger.info(f"Texto extraído: {len(text)} caracteres")
        
        # 2. Construir prompt para el LLM
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un analista financiero experto. "
                    "Tu tarea es resumir informes financieros de forma clara y concisa, "
                    "destacando las métricas clave, tendencias importantes y conclusiones principales."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Resume el siguiente informe financiero. "
                    f"Incluye:\n"
                    f"- Métricas financieras clave\n"
                    f"- Tendencias principales\n"
                    f"- Conclusiones importantes\n\n"
                    f"INFORME:\n{text}"
                )
            }
        ]
        
        # 3. Enviar a Groq para resumir
        logger.info("Enviando a Groq para generar resumen...")
        summary = groq_client.chat(
            messages=messages,
            temperature=0.3,  # Baja temperatura para mayor precisión
            max_tokens=1500   # Resumen extenso pero controlado
        )
        
        logger.info(f"✓ Resumen generado: {len(summary)} caracteres")
        
        return SummarizeResponse(
            filename=request.filename,
            original_length=len(text),
            summary=summary,
            summary_length=len(summary)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al resumir documento: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )
