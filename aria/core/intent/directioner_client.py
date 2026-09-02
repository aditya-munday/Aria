"""Directioner AI Intent API client and Groq tool definitions."""

import asyncio
import json
import logging
import time
from typing import Any

from aria.core.intent.schemas import (
    IntentCategory,
    IntentExecutionResult,
    IntentPayload,
    RiskTier,
)

logger = logging.getLogger(__name__)

DIRECTIONER_TOOL_DEFINITION: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "delegate_to_directioner_ai",
        "description": (
            "Delegate any operating system action, application control, file change, or system "
            "workflow to Directioner AI. Aria NEVER executes system commands directly. Always use "
            "this tool when a system-touching action is needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": [
                        "system_action",
                        "app_control",
                        "file_operation",
                        "media_playback",
                        "canvas_panel",
                        "custom",
                    ],
                    "description": "Category of the intended action.",
                },
                "action_name": {
                    "type": "string",
                    "description": "Descriptive action identifier, e.g., 'open_application', 'delete_file', 'mute_volume'.",
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the action.",
                },
                "risk_tier": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Assessed risk level of the action.",
                },
                "spoken_summary": {
                    "type": "string",
                    "description": "Short spoken explanation of what action will be taken for user transparency.",
                },
            },
            "required": ["category", "action_name", "risk_tier", "spoken_summary"],
        },
    },
}


class DirectionerAIClient:
    """Client for delegating actions across the strict Directioner AI boundary."""

    def __init__(
        self,
        endpoint_url: str | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.timeout_seconds = timeout_seconds
        self._execution_history: list[IntentPayload] = []

    def build_intent_from_tool_call(self, arguments_json: str) -> IntentPayload:
        """Parse Groq tool call arguments into a validated IntentPayload."""
        try:
            data = json.loads(arguments_json)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse tool call arguments JSON: %s", e)
            data = {}

        category_str = data.get("category", "system_action")
        try:
            category = IntentCategory(category_str)
        except ValueError:
            category = IntentCategory.SYSTEM_ACTION

        risk_str = data.get("risk_tier", "low")
        try:
            risk_tier = RiskTier(risk_str)
        except ValueError:
            risk_tier = RiskTier.LOW

        requires_confirmation = risk_tier in (RiskTier.HIGH, RiskTier.CRITICAL)

        return IntentPayload(
            category=category,
            action_name=data.get("action_name", "unknown_action"),
            parameters=data.get("parameters", {}),
            risk_tier=risk_tier,
            requires_confirmation=requires_confirmation,
            spoken_summary=data.get("spoken_summary", ""),
        )

    async def execute_intent(
        self, intent: IntentPayload, confirmed_by_user: bool = False
    ) -> IntentExecutionResult:
        """Forward intent to Directioner AI pipeline (Plan -> Policy -> Reviewer -> Result)."""
        start_time = time.time()
        self._execution_history.append(intent)

        if intent.requires_confirmation and not confirmed_by_user:
            logger.info(
                "Intent %s requires human confirmation before execution.",
                intent.intent_id,
            )
            return IntentExecutionResult(
                intent_id=intent.intent_id,
                status="rejected",
                error="Action requires explicit user confirmation.",
                execution_time_ms=(time.time() - start_time) * 1000.0,
            )

        # Simulation / dispatch to Directioner AI endpoint
        await asyncio.sleep(0.01)

        logger.info(
            "Delegated intent %s [%s: %s] to Directioner AI pipeline.",
            intent.intent_id,
            intent.category.value,
            intent.action_name,
        )

        return IntentExecutionResult(
            intent_id=intent.intent_id,
            status="success",
            output={
                "message": f"Successfully delegated {intent.action_name} to Directioner AI.",
                "action": intent.action_name,
            },
            execution_time_ms=(time.time() - start_time) * 1000.0,
        )
