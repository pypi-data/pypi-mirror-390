"""Python Gemini CLI adapter mirroring the TypeScript package exports."""

__version__ = "0.1.0"

from .adapter import CODER_NAME, GeminiAdapter, create_adapter

__all__ = ["__version__", "CODER_NAME", "GeminiAdapter", "create_adapter"]
