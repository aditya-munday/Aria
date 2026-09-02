"""Data schemas and type definitions for the Directioner AI Intent API."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    """Safety and risk classification for intents."""

    LOW = "low"  # Read-only queries, non-destructive queries
    MEDIUM = "medium"  # Opening apps, minor config tweaks
    HIGH = "high"  # File modifications, deletions, sending messages
    CRITICAL = "critical"  # Terminal command execution, system reboot, wiping data


class IntentCategory(str, Enum):
    """Categorical classification of delegated actions."""

    SYSTEM_ACTION = "system_action"
    APP_CONTROL = "app_control"
    FILE_OPERATION = "file_operation"
    MEDIA_PLAYBACK = "media_playback"
    CANVAS_PANEL = "canvas_panel"
    CUSTOM = "custom"


class IntentPayload(BaseModel):
    """Structured intent representation sent to Directioner AI."""

    intent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: IntentCategory = IntentCategory.SYSTEM_ACTION
    action_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    risk_tier: RiskTier = RiskTier.LOW
    requires_confirmation: bool = False
    spoken_summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntentExecutionResult(BaseModel):
    """Result returned by Directioner AI pipeline after execution."""

    intent_id: str
    status: str  # 'success' | 'cancelled' | 'rejected' | 'failed'
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    execution_time_ms: float = 0.0
