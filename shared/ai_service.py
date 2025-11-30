import os
import json
import logging
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
from .config import (
    GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)
# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Cargar variables de entorno
load_dotenv()
# Prompt Engineering - La "Salsa Secreta"
SYSTEM_PROMPT = (
    """Eres un asistente especializado en gestión de proyectos """
    """y planificación académica.
"""
    """Tu objetivo es ayudar a las personas a convertir """
    """instrucciones vagas en pasos claros y concretos."""
Analiza la siguiente tarea y proporciona tu respuesta en formato JSON válido con esta estructura:
{
  "pasos": [
    "Lista de pasos concretos y accionables para completar la tarea",
    "Cada paso debe comenzar con un verbo de acción",
    "Ejemplo: Definir el alcance del proyecto"
  ],
  "ambiguedades": [
    "Lista de información que falta o no está clara",
    "Ejemplo: No se especifica la fecha de entrega exacta"
  ],
  "preguntas_sugeridas": [
    "Preguntas específicas para clarificar las ambigüedades",
    "Ejemplo: ¿Cuál es el formato requerido para el documento?"
  ]
}
Responde ÚNICAMENTE con el JSON, sin texto adicional antes o después."""
class AIService:
    def __init__(self):
        """
        Inicializa el servicio de IA con Google Gemini.
        Raises:
            ValueError: Si GEMINI_API_KEY no está configurada
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"Gemini inicializado con modelo: {GEMINI_MODEL}")
    def desambiguar_tarea(self, texto_tarea: str) -> Dict[str, Any]:
        prompt_usuario = f"""Analiza la siguiente tarea o instrucción:
"{texto_tarea}"
Desglósala en pasos concretos e identifica qué información falta o es ambigua.
Responde en formato JSON como se indicó."""
        try:
            return self._procesar_con_gemini(prompt_usuario)
        except Exception as e:
            logger.error(f"Error al procesar con Gemini: {str(e)}")
            return {
                "error": f"Error al procesar con Gemini: {str(e)}",
                "pasos": [],
                "ambiguedades": [],
                "preguntas_sugeridas": []
            }
    def _procesar_con_gemini(self, prompt_usuario: str) -> Dict[str, Any]:
        prompt_completo = f"{SYSTEM_PROMPT}\n\nTarea a analizar:\n{prompt_usuario}"
        # Configuración de generación
        generation_config = {
            "temperature": DEFAULT_TEMPERATURE,
            "max_output_tokens": MAX_OUTPUT_TOKENS,
        }
        # Configuración de seguridad - permitir todo
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        response = self.model.generate_content(
            prompt_completo,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        # Verificar el finish_reason
        if response.candidates and len(response.candidates) > 0:
            finish_reason = response.candidates[0].finish_reason
            if finish_reason == 2:  # SAFETY
                # Intentar de nuevo con un prompt más simple
                prompt_simple = f"""Analiza esta tarea y responde en JSON:
Tarea: {prompt_usuario.split(':', 1)[-1].strip().replace('"', '')}
Formato de respuesta (JSON):
{{
  "pasos": ["paso 1", "paso 2", "paso 3"],
  "ambiguedades": ["info faltante 1", "info faltante 2"],
  "preguntas_sugeridas": ["pregunta 1", "pregunta 2"]
}}"""
                response = self.model.generate_content(
                    prompt_simple,
                    generation_config={"temperature": 0.3, "max_output_tokens": 2048},
                    safety_settings=safety_settings
                )
        # Verificar que hay respuesta
        if not response.text:
            finish_reason = (
                response.candidates[0].finish_reason
                if response.candidates
                else 'desconocido'
            )
            raise Exception(
                f"Gemini no generó una respuesta válida. "
                f"Código de finalización: {finish_reason}"
            )
        # Gemini a veces devuelve el JSON dentro de markdown code blocks
        texto = response.text.strip()
        # Limpiar markdown code blocks
        if texto.startswith("```json"):
            texto = texto[7:]
        elif texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()
        # Logging para debug (solo en desarrollo)
        logger.debug(f"Respuesta de Gemini (primeros 500 chars): {texto[:500]}")
        # Intentar parsear JSON con mejor manejo de errores
        try:
            resultado = json.loads(texto)
            logger.info("JSON parseado exitosamente")
            # Validar que tenga las claves necesarias
            required_keys = ["pasos", "ambiguedades", "preguntas_sugeridas"]
            if not all(key in resultado for key in required_keys):
                logger.warning(f"JSON incompleto. Claves presentes: {list(resultado.keys())}")
                # Agregar claves faltantes con valores por defecto
                for key in required_keys:
                    if key not in resultado:
                        resultado[key] = []
            return resultado
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}")
            raise Exception(f"JSON incompleto o mal formado. Por favor, intenta de nuevo.")
# Función auxiliar para testing rápido
def test_ai_service():
    servicio = AIService()
    texto_prueba = "Hacer un ensayo sobre la Segunda Guerra Mundial para el viernes"
    print("Probando De-Mystify...")
    print(f"Tarea: {texto_prueba}\n")
    resultado = servicio.desambiguar_tarea(texto_prueba)
    print("PASOS CONCRETOS:")
    for i, paso in enumerate(resultado["pasos"], 1):
        print(f"{i}. {paso}")
    print("\nINFORMACIÓN FALTANTE:")
    for amb in resultado["ambiguedades"]:
        print(f"- {amb}")
    print("\nPREGUNTAS SUGERIDAS:")
    for preg in resultado.get("preguntas_sugeridas", []):
        print(f"  • {preg}")
if __name__ == "__main__":
    test_ai_service()