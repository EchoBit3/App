__version__ = "1.0.0"
__author__ = "Jean"
from .ai_service import AIService
from .config import (
    GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS,
    APP_TITLE,
    APP_ICON,
    APP_DESCRIPTION,
    EJEMPLOS
)
__all__ = [
    "AIService",
    "GEMINI_MODEL",
    "DEFAULT_TEMPERATURE",
    "MAX_OUTPUT_TOKENS",
    "APP_TITLE",
    "APP_ICON",
    "APP_DESCRIPTION",
    "EJEMPLOS"
]