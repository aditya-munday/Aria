"""Unit tests for Aria unified CLI commands."""

import pytest

from aria.cli import build_parser, main


@pytest.mark.unit
def test_cli_parser_commands() -> None:
    parser = build_parser()

    args_run = parser.parse_args(["run", "--mode", "jarvis", "--query", "Status report"])
    assert args_run.command == "run"
    assert args_run.mode == "jarvis"
    assert args_run.query == "Status report"

    args_config = parser.parse_args(["config", "--set", "voice_id", "aria-v2"])
    assert args_config.command == "config"
    assert args_config.set == ["voice_id", "aria-v2"]

    args_memory = parser.parse_args(["memory", "--stats"])
    assert args_memory.command == "memory"
    assert args_memory.stats is True

    args_overlay = parser.parse_args(["overlay", "--port", "9000"])
    assert args_overlay.command == "overlay"
    assert args_overlay.port == 9000


@pytest.mark.unit
def test_cli_run_command_execution() -> None:
    # Test executing a simulated run turn via main entry point
    exit_code = main(["run", "--mode", "aria", "--query", "Hello test"])
    assert exit_code == 0


@pytest.mark.unit
def test_cli_config_and_memory_execution(tmp_path: pytest.TempPathFactory) -> None:
    db_file = str(tmp_path) + "/test_cli.db"

    # Set preference
    exit_set = main(["config", "--set", "reduce_motion", "true", "--db", db_file])
    assert exit_set == 0

    # Get preference
    exit_get = main(["config", "--get", "reduce_motion", "--db", db_file])
    assert exit_get == 0

    # Memory stats
    exit_stats = main(["memory", "--stats", "--db", db_file])
    assert exit_stats == 0

    # Memory purge
    exit_purge = main(["memory", "--purge", "--db", db_file])
    assert exit_purge == 0

    # Overlay command
    exit_overlay = main(["overlay", "--port", "8765"])
    assert exit_overlay == 0
