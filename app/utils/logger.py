"""
Logger centralizado de la aplicación.
Configura el logging de forma consistente para todos los módulos.
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger.
    
    Args:
        name: Nombre del logger (generalmente __name__ del módulo)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Si ya está configurado, devolverlo
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formato detallado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger ya configurado.
    Útil para obtener el logger en cualquier módulo.
    
    Args:
        name: Nombre del módulo (usa __name__)
    
    Returns:
        Logger del módulo
    """
    return logging.getLogger(name)
