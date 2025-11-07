import os
import base64
from pathlib import Path
from dotenv import load_dotenv

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

import google.generativeai as genai
from openai import OpenAI
import anthropic

from multi_ai_handler.generate_payload import generate_openai_payload, generate_google_payload, generate_claude_payload, generate_ollama_payload

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def _process_file(file: str | Path | dict | None) -> tuple[str | None, str | None]:
    if file is None:
        return None, None

    if isinstance(file, dict):
        return file.get("filename"), file.get("encoded_data")

    file_path = Path(file)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    with open(file_path, "rb") as f:
        file_data = f.read()

    encoded = base64.b64encode(file_data).decode()
    return file_path.name, encoded

def request_google(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, model:str=None, temperature: float=0.0) -> str:
    genai.configure(api_key=GEMINI_API_KEY)

    generative_model = genai.GenerativeModel(model, system_instruction=system_prompt)

    filename, encoded_data = _process_file(file)
    payload: list = generate_google_payload(filename, encoded_data, user_text)

    response = generative_model.generate_content(
        contents=payload,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
        ),
    )

    return response.text

def request_anthropic(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, model:str=None, temperature: float=0.0):
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    filename, encoded_data = _process_file(file)
    messages: list = generate_claude_payload(filename, encoded_data, user_text)

    response: str = ""

    with client.messages.stream(
        model=model,
        max_tokens=20000,
        temperature=temperature,
        system=system_prompt,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            response += text

    return response

def request_openrouter(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, model:str=None, temperature: float=0.0) -> str:
    link: str="https://openrouter.ai/api/v1"
    return request_openai(system_prompt, user_text, file, model, temperature, link)

def request_openai(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, model:str=None, temperature: float=0.0, link:str | None=None) -> str:
    client = OpenAI(
        base_url=link,
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    filename, encoded_data = _process_file(file)
    messages: list = generate_openai_payload(system_prompt, filename, encoded_data, user_text)

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )

    return completion.choices[0].message.content

def request_ollama(system_prompt: str, user_text: str=None, file: str | Path | dict | None=None, model: str=None, temperature: float=0.0) -> str:
    if not OLLAMA_AVAILABLE:
        raise ImportError(
            "Ollama is not installed. Install it with: pip install multi-ai-handler[ollama]"
        )

    filename, encoded_data = _process_file(file)
    messages: list = generate_ollama_payload(system_prompt, filename, encoded_data, user_text)

    response = ollama.chat(
        model=model,
        messages=messages,
        options={"temperature": temperature},
    )

    return response['message']['content']