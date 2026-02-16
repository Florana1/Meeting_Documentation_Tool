"""Configuration loading from .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_config() -> None:
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)


def get_huggingface_token() -> str:
    """Get HuggingFace token from environment."""
    load_config()
    token = os.getenv("HUGGINGFACE_TOKEN", "")
    if not token or token == "hf_...":
        raise ValueError(
            "HUGGINGFACE_TOKEN not set. Add it to your .env file.\n"
            "Get a token at https://huggingface.co/settings/tokens\n"
            "Then accept model terms at:\n"
            "  https://huggingface.co/pyannote/speaker-diarization-3.1\n"
            "  https://huggingface.co/pyannote/segmentation-3.0"
        )
    return token


def get_anthropic_api_key() -> str:
    """Get Anthropic API key from environment."""
    load_config()
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key or key == "sk-ant-...":
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Add it to your .env file.\n"
            "Get a key at https://console.anthropic.com/settings/keys"
        )
    return key
