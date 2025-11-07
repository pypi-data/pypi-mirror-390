import mimetypes
from typing import Any

def generate_openai_payload(system_prompt: str, filename: str | None, encoded_data: str | None, user_text: str | None) -> list[dict[str, Any]]:
    if not filename and not user_text:
        raise ValueError("Either filename or user_text must be provided.")

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    content = []

    if user_text:
        content.append({
            "type": "text",
            "text": user_text
        })

    if filename and encoded_data:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            raise ValueError("Could not detect MIME type from filename.")

        data_url = f"data:{mime_type};base64,{encoded_data}"

        if mime_type.startswith("image/"):
            content.append({
                "type": "image_url",
                "image_url": {"url": data_url}
            })
        elif mime_type == "application/pdf":
            content.append({
                "type": "file",
                "file": {
                    "filename": filename,
                    "file_data": data_url
                }
            })

    messages.append({
        "role": "user",
        "content": content
    })

    return messages

def generate_google_payload(filename: str | None, encoded_data: str | None, user_text: str | None) -> list[dict[str, Any]]:
    if not filename and not user_text:
        raise ValueError("Either filename or user_text must be provided.")

    parts = []

    if user_text:
        parts.append({"text": user_text})

    if filename and encoded_data:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            raise ValueError("Could not detect MIME type from filename.")

        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": encoded_data
            }
        })

    return parts

def generate_claude_payload(filename: str | None, encoded_data: str | None, user_text: str | None) -> list[dict[str, Any]]:
    if not filename and not user_text:
        raise ValueError("Either filename or user_text must be provided.")

    content = []

    if user_text:
        content.append({
            "type": "text",
            "text": user_text
        })

    if filename and encoded_data:
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            raise ValueError("Could not detect MIME type from filename.")

        if mime_type.startswith("image/"):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": encoded_data
                }
            })
        else:
            content.append({
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": encoded_data
                }
            })

    # Return messages array with user message
    messages = [
        {
            "role": "user",
            "content": content
        }
    ]

    return messages
