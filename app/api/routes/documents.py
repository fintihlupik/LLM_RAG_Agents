"""
Rutas para gestión de documentos.
Upload, listado y operaciones con archivos.
"""
from fastapi import APIRouter, UploadFile, File

from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Sube un documento financiero.
    
    Formatos soportados:
    - PDF: Informes, balances, estados financieros
    - Excel (.xlsx, .xls): Hojas de cálculo con datos financieros
    - Word (.docx, .doc): Documentos de análisis
    - CSV: Datos tabulares
    
    El archivo se guarda en uploads/raw con un timestamp único.
    """
    return await document_service.upload_document(file)


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
