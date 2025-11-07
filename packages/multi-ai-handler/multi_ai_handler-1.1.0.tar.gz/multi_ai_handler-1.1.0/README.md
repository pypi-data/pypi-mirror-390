# Multi AI Handler

A unified Python library for interacting with multiple AI providers through a consistent interface. Supports text and file inputs across OpenAI, Anthropic Claude, Google Gemini, OpenRouter, and Ollama (local LLMs).

## Features

- Unified interface for multiple AI providers
- Support for text-only, file-only, or combined text and file inputs
- Automatic payload formatting for each provider's API requirements
- Support for images and documents (PDF)
- Local LLM support with Ollama
- Advanced document processing with Docling (OCR, table extraction)
- Streaming support for Anthropic Claude
- Environment-based API key management
- Optional dependencies for lightweight installations

## Supported Providers

- Anthropic Claude
- Google Gemini
- OpenAI
- OpenRouter
- Ollama (Local LLMs)

## Installation

### Prerequisites

- Python 3.11 or higher

### Basic Installation

```bash
pip install multi-ai-handler
```

This installs the core package with support for Anthropic, Google, OpenAI, and OpenRouter.

### Optional Dependencies

For local LLM support and advanced document processing, install optional dependencies:

```bash
# For Ollama support (local LLMs)
pip install multi-ai-handler[ollama]

# For document processing with Docling (OCR, table extraction)
pip install multi-ai-handler[docling]

# For full local LLM support with document processing
pip install multi-ai-handler[local]

# Install all optional dependencies
pip install multi-ai-handler[all]
```

**Optional features:**
- `ollama` - Local LLM support via Ollama
- `docling` - Advanced document processing (OCR, table extraction) with EasyOCR
- `local` - Both ollama and docling for complete local setup
- `all` - All optional dependencies

## Setup

### 1. Create a `.env` file

Create a `.env` file in your project root with your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 2. Import the library

```python
from multi_ai_handler import (
    request_ai,
    request_anthropic,
    request_google,
    request_openai,
    request_openrouter,
    request_ollama,  # For local LLMs
    Providers
)
```

## Usage

### Text-only requests

```python
from multi_ai_handler import request_anthropic

response = request_anthropic(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?",
    model="claude-3-5-sonnet-20241022",
    temperature=0.7
)
print(response)
```

### Local LLM with Ollama

```python
from multi_ai_handler import request_ollama

# Requires: pip install multi-ai-handler[ollama]
# and Ollama running locally

response = request_ollama(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?",
    model="llama3.2",
    temperature=0.7
)
print(response)
```

### Local document processing with Ollama

```python
from multi_ai_handler import request_ollama

# Requires: pip install multi-ai-handler[local]
# Extracts text from documents using Docling (OCR, tables, etc.)

response = request_ollama(
    system_prompt="You are a document analysis assistant.",
    user_text="Summarize the key points from this document.",
    file="document.pdf",
    model="llama3.2",
    temperature=0.0
)
print(response)
```

### Image analysis

```python
from multi_ai_handler import request_google

# Simply pass the file path
response = request_google(
    system_prompt="You are an image analysis expert.",
    user_text="Describe what you see in this image.",
    file="image.jpg",
    model="gemini-1.5-flash",
    temperature=0.0
)
print(response)
```

### Document processing

```python
from multi_ai_handler import request_anthropic

# Pass the PDF file path
response = request_anthropic(
    system_prompt="You are a document analysis assistant.",
    user_text="Summarize the key points from this document.",
    file="document.pdf",
    model="claude-3-5-sonnet-20241022",
    temperature=0.0
)
print(response)
```

### File-only requests (no text)

```python
from multi_ai_handler import request_google

# User text can be None when only analyzing a file
response = request_google(
    system_prompt="Extract all text and data from images.",
    file="chart.png",
    model="gemini-1.5-pro"
)
print(response)
```

### Using pathlib.Path

```python
from multi_ai_handler import request_anthropic
from pathlib import Path

response = request_anthropic(
    system_prompt="Analyze this document.",
    file=Path("documents/report.pdf"),
    model="claude-3-5-sonnet-20241022"
)
print(response)
```

### Using pre-encoded data

```python
from multi_ai_handler import request_google
import base64

# If you already have encoded data
with open("image.jpg", "rb") as f:
    encoded_data = base64.b64encode(f.read()).decode()

response = request_google(
    system_prompt="Describe this image.",
    file={"filename": "image.jpg", "encoded_data": encoded_data},
    model="gemini-1.5-flash"
)
print(response)
```

### Unified interface with JSON output

The library provides a unified `request_ai()` function that automatically routes to the appropriate provider and supports JSON output parsing:

```python
from multi_ai_handler import request_ai, Providers

# Basic usage with default provider (Google)
response = request_ai(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?",
    temperature=0.7
)
print(response)

# Specify a provider and model
response = request_ai(
    system_prompt="You are a data extraction expert.",
    user_text="Extract key information from: John Doe, age 30, lives in NYC",
    provider=Providers.ANTHROPIC,
    model="claude-sonnet-4-5-20250929",
    temperature=0.0
)
print(response)

# Request JSON output - automatically parses response
data = request_ai(
    system_prompt="You are a JSON formatter. Return valid JSON only.",
    user_text="Convert to JSON: Name: Alice, Age: 25, City: London",
    provider="google",
    json_output=True
)
print(data)  # Returns parsed dict
```

**JSON Output Parsing:**
- When `json_output=True`, the function automatically extracts and parses JSON from the response
- Handles responses wrapped in markdown code blocks (```json ... ```)
- Returns a Python dictionary
- Raises an exception if JSON parsing fails

## API Reference

### Common Parameters

All request functions share the following parameters:

- `system_prompt` (str, required): The system instruction for the AI model
- `user_text` (str, optional): The user's text input
- `file` (str | Path | dict, optional): File to process. Can be:
  - **File path**: `"image.jpg"` or `Path("image.jpg")` - automatically reads and encodes
  - **Dict**: `{"filename": "image.jpg", "encoded_data": "base64..."}` - for pre-encoded data
- `model` (str, required): The specific model to use
- `temperature` (float, optional): Controls randomness (0.0 = deterministic, 1.0 = creative). Default: 0.0

**Note**: Either `user_text` or `file` must be provided.

### `request_anthropic()`

Makes a request to Anthropic's Claude API with streaming support.

```python
def request_anthropic(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    model: str = None,
    temperature: float = 0.0
) -> str
```

**Supported file types**: Images (PNG, JPEG, GIF, WebP), Documents (PDF, DOCX, TXT, etc.)

### `request_google()`

Makes a request to Google's Gemini API with token usage reporting.

```python
def request_google(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    model: str = None,
    temperature: float = 0.0
) -> str
```

**Supported file types**: Images, videos, audio, documents

**Note**: Prints token usage (prompt, output, and total tokens) to console.

### `request_openai()`

Makes a request to OpenAI's API.

```python
def request_openai(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    model: str = None,
    temperature: float = 0.0,
    link: str = None
) -> str
```

**Supported file types**: Images (PNG, JPEG, GIF, WebP), PDFs (via file API)

**Additional parameter**:
- `link` (str, optional): Custom base URL for API endpoint

### `request_openrouter()`

Makes a request through OpenRouter's unified API.

```python
def request_openrouter(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    model: str = None,
    temperature: float = 0.0
) -> str
```

Uses OpenAI-compatible format. Requires `OPENROUTER_API_KEY` in environment.

### `request_ollama()`

Makes a request to a local Ollama instance for running LLMs locally.

```python
def request_ollama(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    model: str = None,
    temperature: float = 0.0
) -> str
```

**Requirements:**
- Install with: `pip install multi-ai-handler[ollama]`
- For document processing: `pip install multi-ai-handler[local]`
- Ollama must be running locally

**Supported file types**: Documents (PDF, DOCX, etc.) via Docling extraction

**Note**: File processing extracts text using Docling (OCR, table extraction) and includes it in the prompt.

### `request_ai()` (Unified Interface)

Unified function that automatically routes to the appropriate provider with built-in JSON parsing support.

```python
def request_ai(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    provider: str | Providers | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    json_output: bool = False
) -> str | dict
```

**Parameters:**
- All common parameters (system_prompt, user_text, file, temperature)
- `provider` (str | Providers, optional): Provider to use. Defaults to Google Gemini
- `model` (str, optional): Model to use. Defaults to first supported model for the provider
- `json_output` (bool, optional): If True, parses and returns JSON as dict. Default: False

**Returns:**
- `str` if `json_output=False`
- `dict` if `json_output=True`

**Supported Providers Enum:**
- `Providers.GOOGLE`
- `Providers.ANTHROPIC`
- `Providers.OPENAI`
- `Providers.OPENROUTER`
- `Providers.OLLAMA`

## Payload Generation

The library automatically formats payloads for each provider using specialized functions:

- `generate_openai_payload()`: Creates OpenAI-compatible content blocks
- `generate_gemini_payload()`: Creates Gemini-compatible parts
- `generate_claude_payload()`: Creates Claude-compatible content blocks
- `generate_ollama_payload()`: Creates Ollama-compatible messages with text extraction

These functions handle:
- MIME type detection from filenames
- Base64 data URL formatting
- Provider-specific content structure
- Document text extraction (Ollama with Docling)
- Validation of required inputs

## Error Handling

The library raises errors in the following cases:

- `ValueError`: Neither `user_text` nor `file` is provided
- `ValueError`: MIME type cannot be detected from filename
- `FileNotFoundError`: File path provided but file doesn't exist
- `ValueError`: Path provided is not a file (e.g., is a directory)
- Invalid API credentials

Example:

```python
from multi_ai_handler import request_anthropic

try:
    response = request_anthropic(
        system_prompt="You are helpful.",
        file="document.pdf",
        model="claude-3-5-sonnet-20241022"
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Use specific model names**: Always specify the exact model version (e.g., `claude-3-5-sonnet-20241022`)
2. **Handle errors**: Wrap API calls in try-except blocks
3. **Manage API keys securely**: Never commit `.env` files to version control
4. **Optimize temperature**: Use lower values (0.0-0.3) for factual tasks, higher (0.7-1.0) for creative tasks

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on the GitHub repository.

