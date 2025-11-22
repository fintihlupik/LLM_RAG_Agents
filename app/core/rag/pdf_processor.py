"""
Servicio de procesamiento de PDFs.
Extracción inteligente de texto con metadata y limpieza de ruido.

Principio: Single Responsibility - Solo se encarga de extraer y limpiar texto.
El chunking está en otro servicio (chunking_service.py).
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import pdfplumber
from fastapi import HTTPException

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFProcessor:
    """
    Procesa PDFs extrayendo texto, metadata y eliminando ruido.
    
    Responsabilidades:
    - Extraer texto página por página
    - Detectar y eliminar headers/footers repetitivos
    - Extraer metadata del documento
    - Preservar estructura (secciones, tablas)
    """
    
    # Patrones de ruido común en PDFs financieros
    NOISE_PATTERNS = [
        r'^Page \d+ of \d+$',  # "Page 1 of 10"
        r'^\d+$',               # Números sueltos (números de página)
        r'^Copyright.*$',       # Copyright notices
        r'^Confidential.*$',    # Confidential notices
        r'^.*proprietary.*$',   # Proprietary notices (case insensitive)
    ]
    
    def __init__(self):
        """Inicializa el procesador."""
        self.upload_dir = Path(settings.upload_dir)
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Optional[str]]:
        """
        Extrae metadata del nombre del archivo.
        
        Formato esperado: company-YYYYMMDD_timestamp.pdf
        Ejemplo: aapl-20250628_20251114_155218.pdf
        
        Args:
            filename: Nombre del archivo
        
        Returns:
            Dict con company y year extraídos
        """
        try:
            # Remover extensión
            name_without_ext = Path(filename).stem
            
            # Patrón: texto-YYYYMMDD_timestamp
            # Ejemplo: aapl-20250628_20251114_155218
            match = re.match(r'^([a-zA-Z0-9\-_]+)-(\d{8})_', name_without_ext)
            
            if match:
                company = match.group(1).upper()  # "AAPL"
                date_str = match.group(2)  # "20250628"
                year = int(date_str[:4])  # 2025
                
                logger.info(f"Metadata extraída: company={company}, year={year}")
                return {"company": company, "year": year}
            
            logger.warning(f"No se pudo extraer metadata del filename: {filename}")
            return {"company": None, "year": None}
            
        except Exception as e:
            logger.warning(f"Error extrayendo metadata del filename: {str(e)}")
            return {"company": None, "year": None}
    
    def _is_noise_line(self, line: str) -> bool:
        """
        Determina si una línea es ruido (header/footer).
        
        Args:
            line: Línea de texto
        
        Returns:
            True si es ruido, False si es contenido útil
        """
        line = line.strip()
        
        # Líneas vacías o muy cortas
        if len(line) < 3:
            return True
        
        # Verificar patrones de ruido
        for pattern in self.NOISE_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia el texto eliminando ruido línea por línea.
        
        Args:
            text: Texto a limpiar
        
        Returns:
            Texto limpio
        """
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            if not self._is_noise_line(line):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def _detect_repeated_headers_footers(self, pages_text: List[str]) -> Tuple[List[str], List[str]]:
        """
        Detecta headers y footers que se repiten en múltiples páginas.
        
        Estrategia: Si las primeras/últimas 3 líneas se repiten en >50% de páginas,
        son headers/footers.
        
        Args:
            pages_text: Lista de textos de cada página
        
        Returns:
            Tupla (headers, footers) con patrones repetitivos
        """
        if len(pages_text) < 3:
            return [], []
        
        # Obtener primeras y últimas 3 líneas de cada página
        first_lines = []
        last_lines = []
        
        for page_text in pages_text:
            lines = [l for l in page_text.split('\n') if l.strip()]
            if lines:
                first_lines.append(lines[:3] if len(lines) >= 3 else lines)
                last_lines.append(lines[-3:] if len(lines) >= 3 else lines)
        
        # Encontrar patrones repetitivos (presentes en >50% de páginas)
        threshold = len(pages_text) * 0.5
        
        # TODO: Implementar lógica de detección si es necesario
        # Por ahora, retornamos vacío (la limpieza por patrones ya funciona)
        
        return [], []
    
    def process_pdf(self, filename: str) -> Dict:
        """
        Procesa un PDF completo: extrae texto, metadata y limpia ruido.
        
        Args:
            filename: Nombre del archivo PDF
        
        Returns:
            Dict con:
                - doc_id: ID único del documento
                - filename: Nombre del archivo
                - company: Empresa (si se puede extraer)
                - year: Año (si se puede extraer)
                - total_pages: Total de páginas
                - pages: Lista de dicts con {page_number, text, tables}
        
        Raises:
            HTTPException: Si hay error al procesar
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
            logger.info(f"Procesando PDF: {filename}")
            
            # Extraer metadata del filename
            file_metadata = self.extract_metadata_from_filename(filename)
            
            # Generar doc_id único
            doc_id = f"{Path(filename).stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            pages_data = []
            
            # Procesar PDF
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"PDF tiene {total_pages} páginas")
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extraer texto de la página
                    text = page.extract_text()
                    
                    if text:
                        # Limpiar ruido
                        clean_text = self._clean_text(text)
                        
                        # Extraer tablas
                        tables = page.extract_tables()
                        formatted_tables = []
                        
                        if tables:
                            for table in tables:
                                formatted_tables.append(self._format_table(table))
                        
                        pages_data.append({
                            "page_number": page_num,
                            "text": clean_text,
                            "tables": formatted_tables,
                            "has_tables": len(formatted_tables) > 0
                        })
                        
                        logger.debug(
                            f"Página {page_num}: {len(clean_text)} caracteres, "
                            f"{len(formatted_tables)} tablas"
                        )
            
            logger.info(
                f"✓ PDF procesado: {total_pages} páginas, "
                f"{len(pages_data)} páginas con contenido"
            )
            
            return {
                "doc_id": doc_id,
                "filename": filename,
                "company": file_metadata["company"],
                "year": file_metadata["year"],
                "total_pages": total_pages,
                "pages": pages_data
            }
            
        except Exception as e:
            logger.error(f"Error al procesar PDF: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al procesar el PDF: {str(e)}"
            )
    
    def _format_table(self, table: List[List]) -> str:
        """
        Formatea una tabla como texto.
        
        Args:
            table: Tabla como lista de listas
        
        Returns:
            Tabla formateada
        """
        if not table:
            return ""
        
        formatted_rows = []
        for row in table:
            formatted_row = [str(cell) if cell is not None else "" for cell in row]
            formatted_rows.append(" | ".join(formatted_row))
        
        return "\n".join(formatted_rows)


# Instancia única
pdf_processor = PDFProcessor()
