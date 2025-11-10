"""
LLM Clients Package
===================

Multiple LLM backend support for Mem-LLM.

Available Backends:
- OllamaClient: Local Ollama service
- LMStudioClient: LM Studio (OpenAI-compatible)
- GeminiClient: Google Gemini API

Author: C. Emre Karataş
Version: 1.3.0
"""

from .ollama_client import OllamaClient
from .lmstudio_client import LMStudioClient
from .gemini_client import GeminiClient

__all__ = [
    'OllamaClient',
    'LMStudioClient',
    'GeminiClient',
]

