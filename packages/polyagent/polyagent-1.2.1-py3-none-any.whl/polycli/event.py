"""Event types for PolyCLI."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ClientEvent:
    """Generic event from any client (Claude, Qwen, Codex, etc.)."""
    session_id: str
    event_type: str  # e.g., "PreToolUse", "PostToolUse", "SessionStart"
    timestamp: datetime
    tool_name: str = None
    tool_input: dict = None
    tool_response: dict = None


# Alias for backward compatibility
ClaudeEvent = ClientEvent