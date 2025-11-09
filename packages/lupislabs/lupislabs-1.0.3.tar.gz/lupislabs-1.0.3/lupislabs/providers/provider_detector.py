from __future__ import annotations

from typing import Optional

from ..types import ProviderHandler, ProviderName
from .anthropic_handler import AnthropicHandler
from .gemini_handler import GeminiHandler
from .openai_handler import OpenAIHandler


def detect_provider(url: str) -> ProviderName:
    if "api.openai.com" in url:
        return "openai"
    if "api.anthropic.com" in url:
        return "claude"
    if "api.cohere.ai" in url:
        return "cohere"
    if "api.huggingface.co" in url:
        return "huggingface"
    if "generativelanguage.googleapis.com" in url:
        return "gemini"
    if "aiplatform.googleapis.com" in url:
        return "gemini"
    if "ai.googleusercontent.com" in url:
        return "gemini"
    if "vertex.googleapis.com" in url:
        return "gemini"
    if "api.google.com" in url:
        return "gemini"
    return "unknown"


def resolve_handler(provider: ProviderName) -> Optional[ProviderHandler]:
    if provider == "openai":
        return OpenAIHandler()
    if provider == "claude":
        return AnthropicHandler()
    if provider in ("gemini", "google"):
        return GeminiHandler()
    return None
