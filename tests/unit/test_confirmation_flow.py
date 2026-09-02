"""Unit tests for the Option A voice & visual confirmation flow manager."""

import time

import pytest

from aria.core.intent.confirmation import (
    ConfirmationManager,
    ConfirmationStatus,
)
from aria.core.intent.schemas import (
    IntentCategory,
    IntentPayload,
    RiskTier,
)


@pytest.mark.unit
def test_confirmation_high_risk_affirmative() -> None:
    manager = ConfirmationManager(default_timeout_seconds=10.0)
    intent = IntentPayload(
        category=IntentCategory.FILE_OPERATION,
        action_name="delete_files",
        risk_tier=RiskTier.HIGH,
        requires_confirmation=True,
    )

    pending = manager.request_confirmation(intent)
    assert pending.status == ConfirmationStatus.PENDING
    assert pending.remaining_seconds > 0.0

    # User says 'Yes' -> CONFIRMED
    status = manager.evaluate_voice_response("Yes, proceed please")
    assert status == ConfirmationStatus.CONFIRMED


@pytest.mark.unit
def test_confirmation_negative_cancellation() -> None:
    manager = ConfirmationManager()
    intent = IntentPayload(
        category=IntentCategory.FILE_OPERATION,
        action_name="wipe_directory",
        risk_tier=RiskTier.HIGH,
        requires_confirmation=True,
    )

    manager.request_confirmation(intent)
    status = manager.evaluate_voice_response("No, cancel that")
    assert status == ConfirmationStatus.CANCELLED


@pytest.mark.unit
def test_confirmation_critical_tier_strict_keyword() -> None:
    manager = ConfirmationManager()
    intent = IntentPayload(
        category=IntentCategory.SYSTEM_ACTION,
        action_name="format_disk",
        risk_tier=RiskTier.CRITICAL,
        requires_confirmation=True,
    )

    manager.request_confirmation(intent)

    # Generic 'yes' is insufficient for CRITICAL
    status_generic = manager.evaluate_voice_response("yes")
    assert status_generic == ConfirmationStatus.PENDING

    # Strict keyword 'confirm format_disk' or 'confirm' approved
    status_strict = manager.evaluate_voice_response("Confirm format disk now")
    assert status_strict == ConfirmationStatus.CONFIRMED


@pytest.mark.unit
def test_confirmation_timeout_auto_abort() -> None:
    manager = ConfirmationManager(default_timeout_seconds=0.05)
    intent = IntentPayload(
        category=IntentCategory.FILE_OPERATION,
        action_name="remove_tree",
        risk_tier=RiskTier.HIGH,
        requires_confirmation=True,
    )

    manager.request_confirmation(intent)
    time.sleep(0.06)

    # Expired timer triggers TIMED_OUT
    status = manager.evaluate_voice_response("Yes")
    assert status == ConfirmationStatus.TIMED_OUT
