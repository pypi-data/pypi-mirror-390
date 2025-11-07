"""Multi AI Handler - Unified interface for multiple AI providers."""

from multi_ai_handler.multi_ai_handler import (
    request_ai,
    parse_ai_response,
    Providers,
    SUPPORTED_MODELS,
)

from multi_ai_handler.ai_handlers import (
    request_anthropic,
    request_google,
    request_openai,
    request_openrouter,
)

__version__ = "1.0.0"

__all__ = [
    # Main unified interface
    "request_ai",
    "parse_ai_response",
    "Providers",
    "SUPPORTED_MODELS",
    # Provider-specific functions
    "request_anthropic",
    "request_google",
    "request_openai",
    "request_openrouter",
]