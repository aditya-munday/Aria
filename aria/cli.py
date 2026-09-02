"""Aria Unified Command-Line Interface (CLI)."""

import argparse
import asyncio
import logging
import sys
from typing import Any

from aria.core.audio.analyzer import AudioAnalyzer
from aria.core.config import ConfigManager
from aria.core.intent.directioner_client import DirectionerAIClient
from aria.core.llm.mock_llm import MockLLMClient
from aria.core.memory.long_term import LongTermMemory
from aria.core.memory.session import SessionMemory
from aria.core.pipeline.orchestrator import PipelineOrchestrator
from aria.core.pipeline.state import AssistantMode
from aria.core.stt.mock_stt import MockStreamingSTT
from aria.core.tts.mock_tts import MockStreamingTTS
from aria.core.vad.mock_vad import MockVADDetector
from aria.core.wake.mock_detector import MockWakeWordDetector
from aria.visual.overlay.server import VisualOverlayServer
from aria.visual.overlay.state_machine import VisualStateMachine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aria.cli")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="aria",
        description="Aria — The AI with Presence (Voice, Dual-Mode Persona, Visual Overlay & Delegation Boundary)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: run
    run_parser = subparsers.add_parser(
        "run", help="Run a voice pipeline turn (interactive or mock)"
    )
    run_parser.add_argument(
        "--mode", choices=["aria", "jarvis"], default="aria", help="Initial assistant mode"
    )
    run_parser.add_argument(
        "--mock", action="store_true", default=True, help="Use mock pipeline engines in CI/testing"
    )
    run_parser.add_argument(
        "--query",
        type=str,
        default="Hello Aria, what is your status?",
        help="User speech input text",
    )

    # Command: benchmark
    subparsers.add_parser("benchmark", help="Run latency and throughput benchmark harness")

    # Command: config
    config_parser = subparsers.add_parser("config", help="View or modify user preferences")
    config_parser.add_argument("--get", type=str, help="Get value of specific preference key")
    config_parser.add_argument(
        "--set", nargs=2, metavar=("KEY", "VALUE"), help="Set preference KEY to VALUE"
    )
    config_parser.add_argument(
        "--db", type=str, default="aria_memory.db", help="SQLite database path"
    )

    # Command: memory
    mem_parser = subparsers.add_parser("memory", help="Manage long-term database memory")
    mem_parser.add_argument(
        "--purge", action="store_true", help="Execute complete privacy purge of all history & facts"
    )
    mem_parser.add_argument(
        "--stats", action="store_true", help="View database memory usage statistics"
    )
    mem_parser.add_argument("--db", type=str, default="aria_memory.db", help="SQLite database path")

    # Command: overlay
    overlay_parser = subparsers.add_parser(
        "overlay", help="Start visual overlay WebSocket bridge server"
    )
    overlay_parser.add_argument("--host", type=str, default="127.0.0.1", help="Server host")
    overlay_parser.add_argument("--port", type=int, default=8765, help="Server port")

    return parser


async def handle_run_command(args: argparse.Namespace) -> int:
    """Execute a single pipeline turn."""
    mode = AssistantMode.JARVIS if args.mode == "jarvis" else AssistantMode.ARIA
    logger.info("Initializing Aria pipeline in %s...", mode.value.upper())

    wake = MockWakeWordDetector()
    vad = MockVADDetector()
    stt = MockStreamingSTT(transcript_to_emit=args.query)
    llm = MockLLMClient()
    tts = MockStreamingTTS()
    analyzer = AudioAnalyzer()
    session_mem = SessionMemory()
    db_mem = LongTermMemory(db_path=":memory:")
    directioner = DirectionerAIClient(memory=db_mem)
    vsm = VisualStateMachine(initial_mode=mode)

    orchestrator = PipelineOrchestrator(
        wake_detector=wake,
        vad_detector=vad,
        stt_client=stt,
        llm_client=llm,
        tts_client=tts,
        audio_analyzer=analyzer,
        session_memory=session_mem,
        long_term_memory=db_mem,
        directioner_client=directioner,
        visual_state_machine=vsm,
    )
    await orchestrator.set_mode(mode)

    async def mock_audio_stream() -> Any:
        for _ in range(5):
            await asyncio.sleep(0.005)
            yield b"\x00\x00" * 256

    response = await orchestrator.run_voice_turn(audio_stream=mock_audio_stream())
    print(f"\n[Aria ({mode.value.upper()})]: {response}\n")
    db_mem.close()
    return 0


def handle_config_command(args: argparse.Namespace) -> int:
    """Manage configuration preferences."""
    mem = LongTermMemory(db_path=args.db)
    mgr = ConfigManager(memory_store=mem)

    if args.set:
        key, val = args.set
        mgr.set_preference(key, val)
        print(f"Updated preference '{key}' = '{val}'")
    elif args.get:
        val = getattr(mgr.config, args.get, None)
        print(f"{args.get}: {val}")
    else:
        print("Aria Current Configuration:")
        for k, v in vars(mgr.config).items():
            print(f"  {k}: {v}")

    mem.close()
    return 0


def handle_memory_command(args: argparse.Namespace) -> int:
    """Manage SQLite database memory."""
    mem = LongTermMemory(db_path=args.db)
    if args.purge:
        mem.clear_all_memory()
        print("Executed complete privacy purge of all database memory.")
    elif args.stats:
        history_count = len(mem.get_recent_history(limit=10000))
        facts_count = len(mem.get_all_facts())
        audit_count = len(mem.get_intent_audit_logs(limit=10000))
        print("Aria Memory Statistics:")
        print(f"  Conversation History Records: {history_count}")
        print(f"  Long-Term User Facts:         {facts_count}")
        print(f"  Delegated Intent Audit Logs:  {audit_count}")
    mem.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "run":
        return asyncio.run(handle_run_command(args))
    elif args.command == "config":
        return handle_config_command(args)
    elif args.command == "memory":
        return handle_memory_command(args)
    elif args.command == "benchmark":
        import pytest

        print("Running Aria latency and throughput benchmark harness...")
        return pytest.main(["-q", "tests/benchmarks/test_latency_benchmark.py"])
    elif args.command == "overlay":
        vsm = VisualStateMachine()
        _ = VisualOverlayServer(state_machine=vsm, host=args.host, port=args.port)
        print(f"Aria Visual Overlay WebSocket server ready at ws://{args.host}:{args.port}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
