"""Mia21 Python SDK - Official client for Mia21 Chat API."""

from .client import Mia21Client, ResponseMode, VoiceConfig
from .portal_client import Mia21PortalClient
from .models import ChatMessage, Space, Tool, ToolCall, StreamEvent
from .exceptions import Mia21Error, ChatNotInitializedError, APIError

__version__ = "1.2.2"  # Version bump for formatting fixes
__all__ = [
    "Mia21Client",
    "Mia21PortalClient",
    "ResponseMode",
    "VoiceConfig",
    "ChatMessage",
    "Space",
    "Tool",
    "ToolCall",
    "StreamEvent",
    "Mia21Error",
    "ChatNotInitializedError",
    "APIError"
]


