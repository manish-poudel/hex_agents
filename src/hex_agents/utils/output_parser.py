from typing import Any

def extract_text(message: Any) -> str:
    content = message.content

    # Most models (Ollama, Qwen, Llama)
    if isinstance(content, str):
        return content

    # Gemini, Anthropic, OpenAI content parts
    if isinstance(content, list):
        texts = []

        for part in content:
            if isinstance(part, dict):
                if "text" in part:
                    texts.append(part["text"])
            elif hasattr(part, "text"):
                texts.append(part.text)
            else:
                texts.append(str(part))

        return "\n".join(texts)

    return str(content)