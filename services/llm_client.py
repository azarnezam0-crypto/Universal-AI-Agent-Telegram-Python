import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "").encode()


def _fernet():
    """Lazily build the Fernet cipher; never crash at import if cryptography
    is missing (e.g. Termux without Rust) or the key is invalid."""
    if not ENCRYPTION_KEY:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(ENCRYPTION_KEY)
    except Exception as e:
        logger.warning(
            "cryptography unavailable or ENCRYPTION_KEY invalid (%s). "
            "API keys will not be encrypted. Generate a key with "
            "cryptography.fernet.Fernet.generate_key().", e
        )
        return None


def encrypt_key(api_key: str) -> str:
    f = _fernet()
    if not f:
        raise ValueError("ENCRYPTION_KEY env var not set or invalid")
    return f.encrypt(api_key.encode()).decode()


def decrypt_key(encrypted: str) -> str:
    f = _fernet()
    if not f:
        raise ValueError("ENCRYPTION_KEY env var not set or invalid")
    return f.decrypt(encrypted.encode()).decode()


def get_client(user) -> OpenAI:
    base_url = user.base_url or os.getenv("DEFAULT_BASE_URL", "https://api.openai.com/v1")
    if user.api_key_encrypted:
        api_key = decrypt_key(user.api_key_encrypted)
    else:
        api_key = os.getenv("DEFAULT_API_KEY", "no-key")
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=90,       # don't hang forever if the endpoint is dead
        max_retries=2,
    )


def fetch_models(user) -> list[str]:
    client = get_client(user)
    models = client.models.list()
    return sorted([m.id for m in models.data])


def chat_completion(user, messages: list[dict]) -> str:
    client = get_client(user)
    model = user.active_model or os.getenv("DEFAULT_MODEL", "gpt-4o")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content


def analyze_image(user, image_base64: str, caption: str) -> str:
    client = get_client(user)
    model = user.active_model or os.getenv("DEFAULT_MODEL", "gpt-4o")
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": caption or "Describe this image in detail."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }],
        max_tokens=1024,
    )
    return response.choices[0].message.content


def transcribe_audio(user, audio_path: str) -> str:
    client = get_client(user)
    with open(audio_path, "rb") as f:
        resp = client.audio.transcriptions.create(model="whisper-1", file=f)
    return resp.text
