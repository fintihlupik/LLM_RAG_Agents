"""
Rutas para gestión de documentos.
Upload, listado y operaciones con archivos.
"""
from fastapi import APIRouter, UploadFile, File, Query
from typing import Optional

from app.services.document_service import document_service
from app.services.analysis_service import analysis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    auto_summarize: Optional[bool] = Query(False, description="Auto-resumir tras subir")
):
    """
    Sube un documento financiero.
    
    Formatos soportados:
    - PDF: Informes, balances, estados financieros
    - Excel (.xlsx, .xls): Hojas de cálculo con datos financieros
    - Word (.docx, .doc): Documentos de análisis
    - CSV: Datos tabulares
    
    Parámetros:
    - file: Archivo a subir
    - auto_summarize: Si es True, resume automáticamente el PDF tras subirlo
    
    Returns:
        Información del archivo subido + resumen (si auto_summarize=True)
    """
    # 1. Subir el archivo
    upload_result = await document_service.upload_document(file)
    
    # 2. Si auto_summarize y es PDF, resumir automáticamente
    if auto_summarize and upload_result["extension"] == ".pdf":
        logger.info(f"Auto-resumiendo: {upload_result['nombre_guardado']}")
        
        try:
            summary_result = await analysis_service.summarize_document(
                upload_result["nombre_guardado"]
            )
            
            # Combinar resultados
            return {
                **upload_result,
                "resumen": summary_result["summary"],
                "auto_resumido": True
            }
        except Exception as e:
            logger.warning(f"No se pudo auto-resumir: {str(e)}")
            # Si falla el resumen, devolver solo la info del upload #graceful degradation. manejo de errores elegante. si el archivo se subio pero la ia fallo no dar error de upload
            return {
                **upload_result,
                "auto_resumido": False,
                "resumen_error": str(e)
            }
    
    return upload_result


@router.get("/")
async def list_documents():
    """
    Lista todos los documentos subidos.
    
    Returns:
        - Lista de documentos con metadata
        - Total de documentos
        - Conteo por tipo de archivo
    """
    return document_service.list_documents()
