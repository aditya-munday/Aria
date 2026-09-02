"""Unit tests for Directioner AI Intent API boundary and safety constraints."""

import json

import pytest

from aria.core.intent.classifier import IntentClassifier
from aria.core.intent.directioner_client import DirectionerAIClient
from aria.core.intent.schemas import IntentCategory, RiskTier


@pytest.mark.unit
def test_intent_classifier() -> None:
    is_intent, cat, risk = IntentClassifier.classify_query("Please delete file document.pdf")
    assert is_intent is True
    assert cat == IntentCategory.FILE_OPERATION
    assert risk == RiskTier.HIGH

    is_intent_critical, cat_c, risk_c = IntentClassifier.classify_query("format drive C:")
    assert is_intent_critical is True
    assert risk_c == RiskTier.CRITICAL

    is_intent_conv, _, _ = IntentClassifier.classify_query("What is the capital of France?")
    assert is_intent_conv is False


@pytest.mark.asyncio
@pytest.mark.unit
async def test_directioner_client_enforces_confirmation_on_high_risk() -> None:
    client = DirectionerAIClient()

    tool_args = json.dumps(
        {
            "category": "file_operation",
            "action_name": "delete_directory",
            "parameters": {"path": "/home/user/downloads"},
            "risk_tier": "high",
            "spoken_summary": "Deleting downloads directory",
        }
    )

    intent = client.build_intent_from_tool_call(tool_args)
    assert intent.requires_confirmation is True
    assert intent.risk_tier == RiskTier.HIGH

    # Execution without confirmation -> rejected
    result_rejected = await client.execute_intent(intent, confirmed_by_user=False)
    assert result_rejected.status == "rejected"
    assert "requires explicit user confirmation" in (result_rejected.error or "")

    # Execution with confirmed_by_user=True -> success
    result_confirmed = await client.execute_intent(intent, confirmed_by_user=True)
    assert result_confirmed.status == "success"
    assert result_confirmed.output.get("action") == "delete_directory"
