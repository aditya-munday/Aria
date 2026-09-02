"""Confirmation flow manager implementing Option A dual-channel voice & visual confirmation."""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

from aria.core.intent.schemas import IntentPayload, RiskTier

logger = logging.getLogger(__name__)


class ConfirmationStatus(str, Enum):
    """Status of a pending confirmation request."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


@dataclass
class PendingConfirmation:
    """Active confirmation request."""

    intent: IntentPayload
    status: ConfirmationStatus = ConfirmationStatus.PENDING
    timeout_seconds: float = 10.0
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0

    def __post_init__(self) -> None:
        if self.expires_at == 0.0:
            self.expires_at = self.created_at + self.timeout_seconds

    @property
    def remaining_seconds(self) -> float:
        """Remaining seconds before auto-abort."""
        return max(0.0, self.expires_at - time.time())

    @property
    def is_expired(self) -> bool:
        """Whether the confirmation timer has elapsed."""
        return time.time() >= self.expires_at


class ConfirmationManager:
    """Manages the lifecycle, voice matching, and timeout of dangerous intent confirmations."""

    AFFIRMATIVE_PHRASES = {
        "yes",
        "proceed",
        "confirm",
        "go ahead",
        "do it",
        "sure",
        "okay",
        "yep",
        "affirmative",
    }

    NEGATIVE_PHRASES = {
        "no",
        "cancel",
        "stop",
        "abort",
        "never mind",
        "don't",
        "nope",
    }

    def __init__(self, default_timeout_seconds: float = 10.0) -> None:
        self.default_timeout_seconds = default_timeout_seconds
        self.active_confirmation: PendingConfirmation | None = None

    def request_confirmation(
        self, intent: IntentPayload, timeout_seconds: float | None = None
    ) -> PendingConfirmation:
        """Create and activate a pending confirmation request."""
        timeout = timeout_seconds or self.default_timeout_seconds
        self.active_confirmation = PendingConfirmation(
            intent=intent,
            timeout_seconds=timeout,
        )
        logger.info(
            "Confirmation requested for intent %s (%s, risk: %s, timeout: %.1fs)",
            intent.intent_id,
            intent.action_name,
            intent.risk_tier.value,
            timeout,
        )
        return self.active_confirmation

    def evaluate_voice_response(self, spoken_text: str) -> ConfirmationStatus:
        """Evaluate a spoken phrase against active confirmation rules."""
        if (
            not self.active_confirmation
            or self.active_confirmation.status != ConfirmationStatus.PENDING
        ):
            return ConfirmationStatus.CANCELLED

        if self.active_confirmation.is_expired:
            self.active_confirmation.status = ConfirmationStatus.TIMED_OUT
            logger.info(
                "Confirmation for intent %s timed out.", self.active_confirmation.intent.intent_id
            )
            return ConfirmationStatus.TIMED_OUT

        cleaned = spoken_text.strip().lower()
        tokens = set(cleaned.replace(",", " ").replace(".", " ").split())

        # Check negative phrases first (exact phrase or word token match)
        if any(neg == cleaned or neg in tokens for neg in self.NEGATIVE_PHRASES):
            self.active_confirmation.status = ConfirmationStatus.CANCELLED
            logger.info(
                "Confirmation for intent %s cancelled by user.",
                self.active_confirmation.intent.intent_id,
            )
            return ConfirmationStatus.CANCELLED

        # For CRITICAL tier actions, require strict keyword confirmation
        if self.active_confirmation.intent.risk_tier == RiskTier.CRITICAL:
            expected_keyword = f"confirm {self.active_confirmation.intent.action_name}".lower()
            if "confirm" in tokens or expected_keyword in cleaned:
                self.active_confirmation.status = ConfirmationStatus.CONFIRMED
                logger.info(
                    "CRITICAL confirmation for intent %s approved.",
                    self.active_confirmation.intent.intent_id,
                )
                return ConfirmationStatus.CONFIRMED
            # Plain yes is insufficient for critical
            return ConfirmationStatus.PENDING

        # For HIGH tier actions, standard affirmatives suffice
        if any(aff == cleaned or aff in tokens for aff in self.AFFIRMATIVE_PHRASES):
            self.active_confirmation.status = ConfirmationStatus.CONFIRMED
            logger.info(
                "Confirmation for intent %s confirmed by voice.",
                self.active_confirmation.intent.intent_id,
            )
            return ConfirmationStatus.CONFIRMED

        return ConfirmationStatus.PENDING

    def clear(self) -> None:
        """Clear active confirmation."""
        self.active_confirmation = None
