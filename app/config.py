"""
Configuración del asistente financiero.
Carga las variables de entorno y valida que estén correctas.
"""
import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación.
    Pydantic valida automáticamente que los valores sean correctos.
    """
    # API de Groq
    groq_api_key: str = Field(..., alias="GROQ_API_KEY") # ... indica que es obligatorio
    
    # Configuración del modelo (cambié model_name a llm_model para evitar warning de Pydantic)
    llm_model: str = Field(default="llama-3.3-70b-versatile", alias="MODEL_NAME")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, alias="TEMPERATURE") # 0.0 >= temp <= 2.0
    max_tokens: int = Field(default=2000, gt=0, alias="MAX_TOKENS") # > 0
    
    # Configuración de la API
    app_name: str = Field(default="Asistente Financiero", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    upload_dir: str = Field(default="./uploads/raw", alias="UPLOAD_DIR")
    
    class Config: # En Pydantic, Config es una clase interna opcional que permite personalizar el comportamiento del modelo, dentro del modelo para que afecte solo esa clase.
        # Le dice a Pydantic que busque variables en el archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Permite usar alias (nombres diferentes) para las variables
        populate_by_name = True # Sin populate_by_name=True, solo funcionaría usando el alias(GROQ_API_KEY - sí, groq_api_key - no)
        # Evita el warning de 'model_' namespace
        protected_namespaces = ()


# Instancia única de configuración para toda la app
settings = Settings()
