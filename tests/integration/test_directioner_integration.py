"""Integration tests for Directioner AI Intent execution and audit log persistence."""

import json

import pytest

from aria.core.intent.directioner_client import DirectionerAIClient
from aria.core.memory.long_term import LongTermMemory


@pytest.mark.asyncio
@pytest.mark.integration
async def test_directioner_audit_log_persistence(
    long_term_memory: LongTermMemory,
) -> None:
    client = DirectionerAIClient(memory=long_term_memory)

    tool_args = json.dumps(
        {
            "category": "app_control",
            "action_name": "launch_editor",
            "parameters": {"file": "main.py"},
            "risk_tier": "medium",
            "spoken_summary": "Opening editor",
        }
    )

    intent = client.build_intent_from_tool_call(tool_args)
    result = await client.execute_intent(intent, confirmed_by_user=True)
    assert result.status == "success"

    # Verify audit record persisted in SQLite
    logs = long_term_memory.get_intent_audit_logs(limit=10)
    assert len(logs) == 1
    assert logs[0]["intent_type"] == "launch_editor"
    assert logs[0]["risk_level"] == "medium"
    assert logs[0]["status"] == "success"
    assert logs[0]["confirmed_by_user"] == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_directioner_audit_log_rejection_record(
    long_term_memory: LongTermMemory,
) -> None:
    client = DirectionerAIClient(memory=long_term_memory)

    tool_args = json.dumps(
        {
            "category": "file_operation",
            "action_name": "delete_all",
            "parameters": {"dir": "/tmp"},
            "risk_tier": "critical",
            "spoken_summary": "Deleting all temporary files",
        }
    )

    intent = client.build_intent_from_tool_call(tool_args)
    result = await client.execute_intent(intent, confirmed_by_user=False)
    assert result.status == "rejected"

    # Verify audit record recorded rejection
    logs = long_term_memory.get_intent_audit_logs(limit=10)
    assert len(logs) == 1
    assert logs[0]["intent_type"] == "delete_all"
    assert logs[0]["risk_level"] == "critical"
    assert logs[0]["status"] == "rejected"
    assert logs[0]["confirmed_by_user"] == 0
