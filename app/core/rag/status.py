"""
Modelos para tracking del estado de procesamiento de documentos.
"""
from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Estados posibles del procesamiento de documentos."""
    PENDING = "pending"           # Recién subido, esperando procesamiento
    PROCESSING = "processing"     # Extrayendo texto y generando chunks
    EMBEDDING = "embedding"       # Generando embeddings (futuro)
    INDEXING = "indexing"         # Indexando en vector store (futuro)
    COMPLETED = "completed"       # Completado y listo para RAG
    FAILED = "failed"             # Error en el procesamiento


class DocumentStatus(BaseModel):
    """
    Estado de procesamiento de un documento.
    Se guarda en memoria (o DB en producción) para tracking.
    """
    doc_id: str = Field(..., description="ID único del documento")
    filename: str = Field(..., description="Nombre del archivo")
    status: ProcessingStatus = Field(..., description="Estado actual")
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    
    # Resultados del procesamiento
    total_chunks: Optional[int] = None
    total_pages: Optional[int] = None
    company: Optional[str] = None
    year: Optional[int] = None
    
    # Tracking de errores
    error_message: Optional[str] = None
    
    # Para RAG (futuro)
    embeddings_generated: bool = False
    indexed_in_vector_store: bool = False


# Storage en memoria (en producción: Redis, Mongo o Postgre)
_document_status_store: dict[str, DocumentStatus] = {}


def save_document_status(status: DocumentStatus):
    """Guarda el estado de un documento."""
    _document_status_store[status.doc_id] = status


def get_document_status(doc_id: str) -> Optional[DocumentStatus]:
    """Obtiene el estado de un documento."""
    return _document_status_store.get(doc_id)


def update_document_status(
    doc_id: str,
    status: Optional[ProcessingStatus] = None,
    **kwargs
):
    """Actualiza el estado de un documento."""
    doc_status = _document_status_store.get(doc_id)
    if doc_status:
        if status:
            doc_status.status = status
        for key, value in kwargs.items():
            if hasattr(doc_status, key):
                setattr(doc_status, key, value)
