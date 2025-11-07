"""
Cliente centralizado para interactuar con Groq LLM.
Gestiona la conexión y comunicación con el modelo de lenguaje.
"""
from groq import Groq
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqClient:
    """
    Cliente para interactuar con la API de Groq.
    Encapsula toda la lógica de comunicación con el LLM.
    """
    
    def __init__(self):
        """Inicializa el cliente de Groq."""
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.llm_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Groq.
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        try:
            logger.info("Probando conexión con Groq...")
            logger.info(f"Modelo: {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente financiero experto."
                    },
                    {
                        "role": "user",
                        "content": "Di 'Conexión exitosa' si me entiendes."
                    }
                ],
                temperature=self.temperature,
                max_tokens=100
            )
            
            respuesta = response.choices[0].message.content
            logger.info(f"Respuesta de Groq: {respuesta}")
            logger.info("✓ Conexión exitosa con Groq")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error al conectar con Groq: {str(e)}")
            return False
    
    def chat(self, messages: list, temperature: float = None, max_tokens: int = None) -> str:
        """
        Envía mensajes al LLM y obtiene respuesta.
        
        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Temperatura para esta llamada (opcional)
            max_tokens: Tokens máximos para esta llamada (opcional)
        
        Returns:
            Respuesta del modelo
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en llamada al LLM: {str(e)}")
            raise


# Instancia única del cliente (Singleton pattern)
groq_client = GroqClient()
