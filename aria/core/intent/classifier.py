"""Fast local intent classification helper."""

from aria.core.intent.schemas import IntentCategory, RiskTier


class IntentClassifier:
    """Classifies queries to determine fast routing between local speech vs tool delegation."""

    @staticmethod
    def classify_query(text: str) -> tuple[bool, IntentCategory, RiskTier]:
        """Determine if query is an intent requiring delegation.

        Returns: (is_delegated_intent, category, risk_tier)
        """
        lower = text.lower()

        # Critical triggers
        if any(w in lower for w in ["format drive", "wipe disk", "delete all files", "rm -rf"]):
            return True, IntentCategory.SYSTEM_ACTION, RiskTier.CRITICAL

        # High risk triggers
        if any(w in lower for w in ["delete file", "remove folder", "uninstall", "kill process"]):
            return True, IntentCategory.FILE_OPERATION, RiskTier.HIGH

        # App / System medium triggers
        if any(
            w in lower for w in ["open app", "launch", "close window", "turn up volume", "mute"]
        ):
            return True, IntentCategory.APP_CONTROL, RiskTier.MEDIUM

        # Conversational / informational (default local)
        return False, IntentCategory.CUSTOM, RiskTier.LOW
