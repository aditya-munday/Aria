"""In-memory session buffer and active context manager."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

from aria.core.pipeline.state import AssistantMode


@dataclass
class ConversationTurn:
    """Individual conversational turn."""

    role: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SessionMemory:
    """Ephemeral session context manager with a bounded turn window (max 50 turns)."""

    def __init__(self, max_turns: int = 50) -> None:
        self.max_turns = max_turns
        self.session_id: str = str(uuid.uuid4())
        self.mode: AssistantMode = AssistantMode.ARIA
        self.turns: list[ConversationTurn] = []
        self.active_panels: list[str] = []
        self.created_at: datetime = datetime.now(timezone.utc)
        self.last_active_at: datetime = datetime.now(timezone.utc)

    def start_new_session(self, mode: AssistantMode = AssistantMode.ARIA) -> None:
        """Start a fresh session identifier and reset ephemeral turns."""
        self.session_id = str(uuid.uuid4())
        self.mode = mode
        self.turns.clear()
        self.active_panels.clear()
        self.created_at = datetime.now(timezone.utc)
        self.last_active_at = datetime.now(timezone.utc)

    def set_mode(self, mode: AssistantMode) -> None:
        """Switch active mode for current session."""
        self.mode = mode
        self.last_active_at = datetime.now(timezone.utc)

    def add_turn(self, role: str, content: str) -> None:
        """Add a conversation turn, evicting oldest if exceeding max_turns bound."""
        self.turns.append(ConversationTurn(role=role, content=content))
        self.last_active_at = datetime.now(timezone.utc)
        if len(self.turns) > self.max_turns:
            self.turns.pop(0)

    def add_panel(self, panel_id: str) -> None:
        """Register active canvas panel."""
        if panel_id not in self.active_panels:
            self.active_panels.append(panel_id)

    def remove_panel(self, panel_id: str) -> None:
        """Unregister canvas panel."""
        if panel_id in self.active_panels:
            self.active_panels.remove(panel_id)

    def get_messages_for_llm(self) -> list[dict[str, str]]:
        """Format turns as message payload for Groq chat completion."""
        return [{"role": turn.role, "content": turn.content} for turn in self.turns]

    def get_recent_context_summary(self, max_items: int = 6) -> str:
        """Format recent turns for prompt context injection."""
        recent = self.turns[-max_items:]
        return "\n".join(f"{t.role.capitalize()}: {t.content}" for t in recent)
