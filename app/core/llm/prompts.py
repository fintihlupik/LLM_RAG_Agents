"""
Templates de prompts para el LLM.
Centraliza todos los prompts reutilizables.

Principio: Separar la lógica de prompts de la lógica de negocio.
"""
from typing import List, Dict


class FinancialPrompts:
    """
    Prompts especializados para análisis financiero.
    """
    
    @staticmethod
    def get_system_prompt() -> str:
        """
        Prompt de sistema para el asistente financiero.
        Define el rol y comportamiento base.
        """
        return (
            "Eres un analista financiero experto con amplia experiencia en "
            "interpretación de informes trimestrales y anuales de empresas. "
            "Tu análisis es preciso, objetivo y se centra en métricas clave. "
            "Siempre destacas tendencias importantes y conclusiones accionables."
        )
    
    @staticmethod
    def build_summarize_prompt(document_text: str) -> List[Dict[str, str]]:
        """
        Construye el prompt para resumir un informe financiero.
        
        Args:
            document_text: Texto extraído del documento
        
        Returns:
            Lista de mensajes en formato OpenAI
        """
        return [
            {
                "role": "system",
                "content": FinancialPrompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": (
                    "Resume el siguiente informe financiero de forma estructurada.\n\n"
                    "Incluye:\n"
                    "1. **Resumen Ejecutivo** (2-3 líneas)\n"
                    "2. **Métricas Clave** (ingresos, beneficios, márgenes, etc.)\n"
                    "3. **Tendencias Principales** (cambios significativos)\n"
                    "4. **Riesgos u Observaciones** (si los hay)\n"
                    "5. **Conclusión** (1-2 líneas)\n\n"
                    f"INFORME:\n{document_text}"
                )
            }
        ]
    
    @staticmethod
    def build_comparison_prompt(doc1_text: str, doc2_text: str) -> List[Dict[str, str]]:
        """
        Construye prompt para comparar dos informes.
        (Para futuro)
        
        Args:
            doc1_text: Texto del primer documento
            doc2_text: Texto del segundo documento
        
        Returns:
            Lista de mensajes
        """
        return [
            {
                "role": "system",
                "content": FinancialPrompts.get_system_prompt()
            },
            {
                "role": "user",
                "content": (
                    "Compara estos dos informes financieros y destaca las diferencias clave.\n\n"
                    f"DOCUMENTO 1:\n{doc1_text}\n\n"
                    f"DOCUMENTO 2:\n{doc2_text}"
                )
            }
        ]
