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
from multi_ai_handler import request_ai
```

## Usage

### Using `request_ai()` (Recommended)

The `request_ai()` function provides a unified interface across all providers with automatic routing and JSON parsing support.

#### Basic text request

```python
from multi_ai_handler import request_ai

# Uses default provider (Google Gemini)
response = request_ai(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?"
)
print(response)
```

#### Specify a provider and model

```python
# Provider specified as string
response = request_ai(
    system_prompt="You are a data extraction expert.",
    user_text="Extract key information from: John Doe, age 30, lives in NYC",
    provider="anthropic",
    model="claude-sonnet-4-5-20250929"
)
```

Supported providers: `"google"`, `"anthropic"`, `"openai"`, `"openrouter"`, `"ollama"`

#### JSON output parsing

```python
# Automatically parses JSON from response
data = request_ai(
    system_prompt="You are a JSON formatter. Return valid JSON only.",
    user_text="Convert to JSON: Name: Alice, Age: 25, City: London",
    json_output=True
)
print(data)  # Returns parsed dict: {'name': 'Alice', 'age': 25, 'city': 'London'}
```

#### File processing (images and documents)

```python
# With images
response = request_ai(
    system_prompt="You are an image analysis expert.",
    user_text="Describe what you see in this image.",
    file="image.jpg",
    provider="google"
)

# With documents
response = request_ai(
    system_prompt="Summarize this document.",
    file="document.pdf",
    provider="anthropic"
)

# Using pathlib.Path
from pathlib import Path
response = request_ai(
    system_prompt="Analyze this document.",
    file=Path("documents/report.pdf"),
    provider="anthropic"
)
```

#### Local LLM with Ollama

```python
# Requires: pip install multi-ai-handler[ollama]
response = request_ai(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?",
    provider="ollama",
    model="llama3.2"
)
```

### Using Provider-Specific Functions

For direct access to provider-specific features, you can use individual functions. All provider functions share the same parameter structure:

```python
from multi_ai_handler import (
    request_anthropic,
    request_google,
    request_openai,
    request_openrouter,
    request_ollama
)
```

#### Examples

**Anthropic Claude** (with streaming support):
```python
response = request_anthropic(
    system_prompt="You are a helpful assistant.",
    user_text="What is the capital of France?",
    model="claude-3-5-sonnet-20241022",
    temperature=0.7
)
```

**Google Gemini** (with token usage reporting):
```python
response = request_google(
    system_prompt="Analyze this image.",
    file="image.jpg",
    model="gemini-1.5-flash"
)
```

**OpenAI** (with custom endpoint support):
```python
response = request_openai(
    system_prompt="You are helpful.",
    user_text="Hello!",
    model="gpt-4",
    link="https://custom-endpoint.com"  # Optional custom base URL
)
```

**Ollama** (with local document processing):
```python
# Requires: pip install multi-ai-handler[local]
response = request_ollama(
    system_prompt="Summarize this document.",
    file="document.pdf",  # Uses Docling for OCR and table extraction
    model="llama3.2"
)
```

## API Reference

### `request_ai()` (Unified Interface)

**Recommended** - Unified function that automatically routes to the appropriate provider with built-in JSON parsing support.

```python
def request_ai(
    system_prompt: str,
    user_text: str = None,
    file: str | Path | dict = None,
    provider: str = None,
    model: str = None,
    temperature: float = 0.2,
    json_output: bool = False
) -> str | dict
```

**Parameters:**
- `system_prompt` (str, required): The system instruction for the AI model
- `user_text` (str, optional): The user's text input
- `file` (str | Path | dict, optional): File to process. Can be:
  - **File path**: `"image.jpg"` or `Path("image.jpg")` - automatically reads and encodes
  - **Dict**: `{"filename": "image.jpg", "encoded_data": "base64..."}` - for pre-encoded data
- `provider` (str, optional): Provider name - `"google"`, `"anthropic"`, `"openai"`, `"openrouter"`, or `"ollama"`. Defaults to `"google"`
- `model` (str, optional): Model to use. Defaults to first supported model for the provider
- `temperature` (float, optional): Controls randomness (0.0 = deterministic, 1.0 = creative). Default: 0.2
- `json_output` (bool, optional): If True, parses and returns JSON as dict. Default: False

**Returns:**
- `str` if `json_output=False`
- `dict` if `json_output=True`

**Note**: Either `user_text` or `file` must be provided.

---

### Direct Provider Functions

For advanced use cases requiring specific provider features, use these functions directly.

#### Common Parameters

All direct provider functions share these parameters:

- `system_prompt` (str, required): The system instruction for the AI model
- `user_text` (str, optional): The user's text input
- `file` (str | Path | dict, optional): File to process (formats same as above)
- `model` (str, required): The specific model to use
- `temperature` (float, optional): Controls randomness. Default: 0.0

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

---

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
from multi_ai_handler import request_ai

try:
    response = request_ai(
        system_prompt="You are helpful.",
        file="document.pdf",
        provider="anthropic",
        model="claude-3-5-sonnet-20241022"
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Error: {e}")
```

## Best Practices

1. **Use `request_ai()` for most tasks**: The unified interface provides consistent behavior across all providers
2. **Use specific model names**: Always specify the exact model version when needed (e.g., `claude-3-5-sonnet-20241022`)
3. **Handle errors**: Wrap API calls in try-except blocks
4. **Manage API keys securely**: Never commit `.env` files to version control
5. **Optimize temperature**: Use lower values (0.0-0.3) for factual tasks, higher (0.7-1.0) for creative tasks

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open an issue on the GitHub repository.

