import json
from pathlib import Path

from multi_ai_handler.ai_handlers import request_openrouter, request_google, request_anthropic, request_openai, request_ollama
from enum import Enum, auto

class LowercaseEnum(str, Enum):
    def _generate_next_value_(self, start, count, last_values):
        return self.lower()

class Providers(LowercaseEnum):
    GOOGLE = auto()
    ANTHROPIC = auto()
    OPENAI = auto()
    OPENROUTER = auto()
    OLLAMA = auto()

SUPPORTED_MODELS = {
    Providers.GOOGLE: ["gemini-2.5-pro", "gemini-2.5-flash"],
    Providers.ANTHROPIC: ['claude-sonnet-4-5-20250929', 'claude-opus-4-1-20250805'],
    Providers.OPENAI: ['gpt-5', 'gpt-4o'],
    Providers.OPENROUTER: ['google/gemini-2.5-pro', 'google/gemini-2.5-flash', 'anthropic/claude-sonnet-4.5', 'anthropic/claude-opus-4.1'],
    Providers.OLLAMA: ['gpt-oss:20b']
}

PROVIDER_FUNCTIONS = {
    Providers.GOOGLE: request_google,
    Providers.ANTHROPIC: request_anthropic,
    Providers.OPENAI: request_openai,
    Providers.OPENROUTER: request_openrouter,
    Providers.OLLAMA: request_ollama
}

def request_ai(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, provider: str | Providers | None = None, model:str | None=None, temperature: float=0.2, json_output: bool = False) -> dict | str:
    if provider is None:
        provider = Providers.GOOGLE
    else:
        provider = Providers(provider)

    if model is None:
        model = SUPPORTED_MODELS[provider][0]

    response_text: str = PROVIDER_FUNCTIONS[provider](system_prompt, user_text, file, model, temperature)

    if json_output:
        return parse_ai_response(response_text)

    else:
        return response_text


def parse_ai_response(response_text: str) -> dict:
    response_text = response_text.strip()
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        start: int = 0
        if "```json" in response_text:
            start = response_text.find("```json") + 7
        elif "```" in response_text:
            start = response_text.find("```") + 3

        if start != 0:
            end: int = response_text.find("```", start)
            if end != -1:
                response_text = response_text[start:end]

    try:
        return json.loads(response_text)
    except json.decoder.JSONDecodeError as e:
        raise Exception(e)