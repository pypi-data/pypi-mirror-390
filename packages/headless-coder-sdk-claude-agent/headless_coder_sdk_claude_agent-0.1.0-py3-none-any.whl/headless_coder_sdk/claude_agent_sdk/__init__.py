"""Python Claude Agent SDK adapter entry point."""

__version__ = "0.1.0"

from .adapter import CODER_NAME, ClaudeAdapter, create_adapter

__all__ = ["__version__", "CODER_NAME", "ClaudeAdapter", "create_adapter"]
