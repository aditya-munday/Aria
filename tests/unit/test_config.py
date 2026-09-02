"""Unit tests for configuration manager and SQLite preferences synchronization."""

import pytest

from aria.core.config import ConfigManager
from aria.core.memory.long_term import LongTermMemory
from aria.core.pipeline.state import AssistantMode


@pytest.mark.unit
def test_config_defaults_and_updates(long_term_memory: LongTermMemory) -> None:
    config_mgr = ConfigManager(memory_store=long_term_memory)

    assert config_mgr.config.default_mode == AssistantMode.ARIA
    assert config_mgr.config.reduce_motion is False

    # Update preferences
    config_mgr.set_preference("default_mode", AssistantMode.JARVIS)
    config_mgr.set_preference("reduce_motion", True)
    config_mgr.set_preference("voice_id", "jarvis-british-v2")

    assert config_mgr.config.default_mode == AssistantMode.JARVIS
    assert config_mgr.config.reduce_motion is True
    assert config_mgr.config.voice_id == "jarvis-british-v2"

    # Reload from same database store
    new_mgr = ConfigManager(memory_store=long_term_memory)
    assert new_mgr.config.default_mode == AssistantMode.JARVIS
    assert new_mgr.config.reduce_motion is True
    assert new_mgr.config.voice_id == "jarvis-british-v2"
