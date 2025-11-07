"""
Punto de entrada principal del asistente financiero.
Por ahora solo verifica que la configuración funciona y conecta con Groq.
"""
import logging
from groq import Groq
from app.config import settings

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def test_groq_connection():
    """
    Prueba básica de conexión con Groq.
    Hace una pregunta simple para verificar que todo funciona.
    """
    try:
        logger.info("Iniciando conexión con Groq...")
        logger.info(f"Modelo configurado: {settings.llm_model}")
        
        # Inicializar cliente de Groq (solo con api_key, sin otros parámetros)
        client = Groq(api_key=settings.groq_api_key)
        
        # Hacer una pregunta de prueba
        logger.info("Enviando mensaje de prueba...")
        response = client.chat.completions.create(
            model=settings.llm_model,
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
            temperature=settings.temperature,
            max_tokens=100
        )
        
        respuesta = response.choices[0].message.content
        logger.info(f"Respuesta de Groq: {respuesta}")
        logger.info("✓ Conexión exitosa con Groq")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Error al conectar con Groq: {str(e)}")
        return False


def main():
    """
    Función principal.
    Por ahora solo prueba la conexión.
    """
    logger.info("=== Asistente Financiero ===")
    logger.info("Iniciando aplicación...")
    
    # Verificar que la configuración se cargó correctamente
    logger.info(f"Configuración cargada: Modelo={settings.llm_model}, Temp={settings.temperature}")
    
    # Probar conexión
    if test_groq_connection():
        logger.info("Sistema listo para usar")
    else:
        logger.error("Hay problemas con la configuración. Revisa tu .env")


if __name__ == "__main__":
    main()
