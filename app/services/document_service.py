"""
Servicio de gestión de documentos.
Encapsula toda la lógica de negocio relacionada con documentos.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import UploadFile, HTTPException

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService:
    """
    Servicio para manejar operaciones con documentos.
    Separar la lógica de negocio de las rutas (routes).
    """
    
    # Extensiones permitidas y sus tipos
    ALLOWED_EXTENSIONS = {
        '.pdf': 'PDF',
        '.xlsx': 'Excel',
        '.xls': 'Excel',
        '.docx': 'Word',
        '.doc': 'Word',
        '.csv': 'CSV'
    }
    
    def __init__(self):
        """Inicializa el servicio de documentos."""
        self.upload_dir = Path(settings.upload_dir)
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self):
        """Asegura que el directorio de uploads existe."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de uploads: {self.upload_dir}")
    
    async def upload_document(self, file: UploadFile) -> Dict:
        """
        Guarda un documento subido.
        
        Args:
            file: Archivo subido por FastAPI
        
        Returns:
            Información del archivo guardado
        
        Raises:
            HTTPException: Si el formato no es válido o hay error al guardar
        """
        # Validar extensión
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado. Extensiones permitidas: {', '.join(self.ALLOWED_EXTENSIONS.keys())}"
            )
        
        file_type = self.ALLOWED_EXTENSIONS[file_ext]
        
        # Generar nombre único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = self.upload_dir / filename
        
        # Guardar archivo
        try:
            logger.info(f"Guardando archivo {file_type}: {filename}")
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            file_size = len(content)
            logger.info(f"✓ Archivo guardado: {file_size} bytes")
            
            return {
                "mensaje": "Archivo subido exitosamente",
                "nombre_original": file.filename,
                "nombre_guardado": filename,
                "tipo": file_type,
                "extension": file_ext,
                "tamaño_bytes": file_size,
                "ruta": str(file_path),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Error al guardar archivo: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al guardar el archivo: {str(e)}"
            )
    
    def list_documents(self) -> Dict:
        """
        Lista todos los documentos en el directorio de uploads.
        
        Returns:
            Diccionario con lista de documentos y estadísticas
        """
        try:
            # Verificar que el directorio existe
            if not self.upload_dir.exists():
                self._ensure_upload_dir()
                return {"documentos": [], "total": 0, "por_tipo": {}}
            
            # Verificar que es un directorio
            if not self.upload_dir.is_dir():
                raise HTTPException(
                    status_code=500,
                    detail=f"La ruta de uploads no es un directorio válido: {self.upload_dir}"
                )
            
            documentos = []
            
            # Iterar sobre archivos
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    
                    if ext in self.ALLOWED_EXTENSIONS:
                        stat = file_path.stat()
                        documentos.append({
                            "nombre": file_path.name,
                            "tipo": self.ALLOWED_EXTENSIONS[ext],
                            "extension": ext,
                            "tamaño_bytes": stat.st_size,
                            "fecha_subida": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            # Ordenar por fecha (más reciente primero)
            documentos.sort(key=lambda x: x["fecha_subida"], reverse=True)
            
            # Contar por tipo
            tipos_count = {}
            for doc in documentos:
                tipo = doc["tipo"]
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
            logger.info(f"Listados {len(documentos)} documentos")
            
            return {
                "documentos": documentos,
                "total": len(documentos),
                "por_tipo": tipos_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error al listar documentos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al listar documentos: {str(e)}"
            )


# Instancia única del servicio (Singleton pattern)
document_service = DocumentService()
