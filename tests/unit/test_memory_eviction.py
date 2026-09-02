"""Unit tests for SQLite memory retention, FIFO/LRU eviction, and privacy purge."""

import pytest

from aria.core.memory.long_term import LongTermMemory
from aria.core.memory.session import SessionMemory
from aria.core.pipeline.state import AssistantMode


@pytest.mark.unit
def test_session_memory_turn_bound() -> None:
    session = SessionMemory(max_turns=3)
    session.add_turn("user", "Turn 1")
    session.add_turn("assistant", "Turn 2")
    session.add_turn("user", "Turn 3")
    assert len(session.turns) == 3

    session.add_turn("assistant", "Turn 4")
    assert len(session.turns) == 3
    assert session.turns[0].content == "Turn 2"
    assert session.turns[-1].content == "Turn 4"


@pytest.mark.unit
def test_long_term_memory_history_fifo_eviction() -> None:
    mem = LongTermMemory(db_path=":memory:", max_history_entries=3)
    session_id = "test-session"

    mem.save_turn(session_id, AssistantMode.ARIA, "user", "Message 1")
    mem.save_turn(session_id, AssistantMode.ARIA, "assistant", "Message 2")
    mem.save_turn(session_id, AssistantMode.ARIA, "user", "Message 3")

    history = mem.get_recent_history(limit=10)
    assert len(history) == 3
    assert history[0]["content"] == "Message 1"

    # Add 4th message and trigger retention eviction
    mem.save_turn(session_id, AssistantMode.ARIA, "assistant", "Message 4")
    evicted = mem.enforce_retention_policy()
    assert evicted == 1

    history_after = mem.get_recent_history(limit=10)
    assert len(history_after) == 3
    assert history_after[0]["content"] == "Message 2"
    assert history_after[-1]["content"] == "Message 4"
    mem.close()


@pytest.mark.unit
def test_long_term_memory_facts_lru_bounding() -> None:
    mem = LongTermMemory(db_path=":memory:", max_facts_entries=2)

    mem.set_fact("favorite_genre", "jazz")
    mem.set_fact("favorite_editor", "neovim")
    assert len(mem.get_all_facts()) == 2

    # Add 3rd fact -> least accessed fact gets evicted
    mem.set_fact("preferred_language", "python")
    facts = mem.get_all_facts()
    assert len(facts) <= 2
    assert "preferred_language" in facts
    mem.close()


@pytest.mark.unit
def test_long_term_memory_privacy_purge() -> None:
    mem = LongTermMemory(db_path=":memory:")
    mem.save_turn("s1", AssistantMode.JARVIS, "user", "Sensitive query")
    mem.set_fact("user_name", "Aditya")
    mem.set_preference("theme", "dark")

    assert len(mem.get_recent_history()) == 1
    assert len(mem.get_all_facts()) == 1

    # Execute privacy purge
    mem.clear_all_memory()

    assert len(mem.get_recent_history()) == 0
    assert len(mem.get_all_facts()) == 0
    assert mem.get_preference("theme") is None
    mem.close()
