"""
Servicio de análisis con LLM.
Encapsula la lógica de negocio para análisis de documentos.

Principio: Single Responsibility - Este servicio solo coordina análisis.
La extracción de texto está en document_service.
Los prompts están en llm/prompts.
"""
from typing import Dict

from fastapi import HTTPException

from app.services.document_service import document_service
from app.core.llm.client import groq_client
from app.core.llm.prompts import FinancialPrompts
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """
    Servicio para análisis de documentos con LLM.
    
    Responsabilidades:
    - Orquestar el proceso de análisis
    - Validar inputs
    - Coordinar servicios (document_service + groq_client)
    - Manejar errores de negocio
    """
    
    def __init__(self):
        """Inicializa el servicio de análisis."""
        self.prompts = FinancialPrompts()
    
    async def summarize_document(self, filename: str) -> Dict:
        """
        Resume un documento PDF usando LLM.
        
        Proceso:
        1. Extrae texto del PDF (delega a document_service)
        2. Construye prompt (delega a prompts)
        3. Llama al LLM (delega a groq_client)
        4. Formatea respuesta
        
        Args:
            filename: Nombre del archivo en uploads/raw
        
        Returns:
            Dict con resumen y estadísticas
        
        Raises:
            HTTPException: Si hay error en el proceso
        """
        try:
            logger.info(f"Iniciando resumen de: {filename}")
            
            # 1. Extraer texto del PDF
            text = document_service.extract_text_from_pdf(filename)
            
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="El PDF no contiene texto extraíble"
                )
            
            logger.info(f"Texto extraído: {len(text)} caracteres")
            
            # 2. Construir prompt
            messages = self.prompts.build_summarize_prompt(text)
            
            # 3. Enviar a LLM
            logger.info("Generando resumen con LLM...")
            summary = groq_client.chat(
                messages=messages,
                temperature=0.3,  # Baja para precisión
                max_tokens=1500
            )
            
            logger.info(f"✓ Resumen generado: {len(summary)} caracteres")
            
            # 4. Formatear respuesta
            return {
                "filename": filename,
                "original_length": len(text),
                "summary": summary,
                "summary_length": len(summary),
                "model_used": groq_client.model
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al resumir documento: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar la solicitud: {str(e)}"
            )


# Instancia única del servicio (Singleton)
analysis_service = AnalysisService()
