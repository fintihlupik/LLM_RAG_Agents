"""
Servicio de gestión de documentos.
Encapsula toda la lógica de negocio relacionada con documentos.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import UploadFile, HTTPException
import pdfplumber

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
        Guarda un documento subido y genera su doc_id único.
        
        Responsabilidad única (SRP): manejo completo del ciclo de vida del upload.
        
        Args:
            file: Archivo subido por FastAPI
        
        Returns:
            Info del archivo guardado + doc_id para tracking
        
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
        
        # Generar nombre único: nombre_original_timestamp.ext
        # Ejemplo: aapl-20250628_20251114_132722.pdf
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = Path(file.filename).stem
        filename = f"{original_name}_{timestamp}{file_ext}"
        file_path = self.upload_dir / filename
        
        # Generar doc_id (SRP: service genera identificadores, no el controller)
        doc_id = self._generate_doc_id(filename)
        
        # Guardar archivo
        try:
            logger.info(f"Guardando archivo {file_type}: {filename}")
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            file_size = len(content)
            logger.info(f"✓ Archivo guardado: {file_size} bytes, doc_id={doc_id}")
            
            return {
                "mensaje": "Archivo subido exitosamente",
                "doc_id": doc_id,
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
    
    def _generate_doc_id(self, filename: str) -> str:
        """
        Genera un ID único para un documento.
        
        Formato: {nombre_sin_extension}_{timestamp_millis}
        Ejemplo: aapl-20250628_20251119153045
        
        Args:
            filename: Nombre del archivo guardado
        
        Returns:
            doc_id único
        """
        stem = Path(filename).stem
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{stem}_{timestamp}"
    
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
    
    def extract_text_from_pdf(self, filename: str) -> str:
        """
        Extrae el texto completo de un PDF usando pdfplumber.
        
        pdfplumber es superior a pypdf porque:
        - Extrae texto con mejor precisión
        - Detecta y preserva tablas
        - Mantiene estructura y formato
        - Ideal para informes financieros con datos tabulares
        
        Args:
            filename: Nombre del archivo PDF en uploads/raw
        
        Returns:
            Texto extraído del PDF con estructura preservada
        
        Raises:
            HTTPException: Si el archivo no existe o no se puede leer
        """
        file_path = self.upload_dir / filename
        
        # Verificar que existe
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Archivo no encontrado: {filename}"
            )
        
        # Verificar que es PDF
        if file_path.suffix.lower() != '.pdf':
            raise HTTPException(
                status_code=400,
                detail=f"El archivo no es un PDF: {filename}"
            )
        
        try:
            logger.info(f"Extrayendo texto de: {filename}")
            
            text_parts = []
            
            # Abrir PDF con pdfplumber (context manager - cierra automáticamente)
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF tiene {total_pages} páginas")
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extraer texto de la página
                    text = page.extract_text()
                    
                    if text and text.strip():
                        text_parts.append(f"--- Página {page_num} ---\n{text}")
                        logger.debug(f"Página {page_num}: {len(text)} caracteres")
                    
                    # Extraer tablas si existen
                    tables = page.extract_tables()
                    if tables:
                        logger.debug(f"Página {page_num}: {len(tables)} tabla(s) detectada(s)")
                        for table_num, table in enumerate(tables, start=1):
                            # Convertir tabla a texto formateado
                            table_text = self._format_table(table)
                            text_parts.append(f"\n[TABLA {table_num}]\n{table_text}")
            
            # Unir todo el texto
            full_text = "\n\n".join(text_parts)
            
            logger.info(f"✓ Texto extraído: {len(full_text)} caracteres de {total_pages} páginas")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error al extraer texto del PDF: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar el PDF: {str(e)}"
            )
    
    def _format_table(self, table: List[List]) -> str:
        """
        Formatea una tabla extraída como texto legible.
        
        Args:
            table: Tabla como lista de listas (filas y columnas)
        
        Returns:
            Tabla formateada como texto
        """
        if not table:
            return ""
        
        # Convertir None a string vacío
        formatted_rows = []
        for row in table:
            formatted_row = [str(cell) if cell is not None else "" for cell in row]
            formatted_rows.append(" | ".join(formatted_row))
        
        return "\n".join(formatted_rows)


# Instancia única del servicio (Singleton pattern)
document_service = DocumentService()
