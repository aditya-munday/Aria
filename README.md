# Aria

> **Living Presence Voice Assistant — Dual-Mode (Aria / Jarvis)**

Aria is a voice assistant engineered for low latency, dual-mode presence (soft Siri-like Aria Mode vs authoritative Iron Man HUD Jarvis Mode), strict local-first safety, and zero-compromise execution boundaries.

---

## 🔒 Mandatory Pipeline Architecture

The runtime voice pipeline follows a strict, non-negotiable order:

```
Microphone
    ↓
[1] openWakeWord          ← dual models ("Aria" / "Jarvis")
    ↓
[2] Silero VAD            ← end-of-utterance + noise robustness
    ↓
[3] smallest.ai STT       ← streaming transcription
    ↓
[4] Groq (LPU)            ← system prompts + tools + database memory
    ↓
[5] smallest.ai TTS       ← streaming audio out
    ↓
[6] Audio Analysis        ← amplitude / pitch / beat → drives visuals
    ↓
Visual Overlay + Canvas + Advanced Vision Control
```

All system actions **must** delegate to the Directioner AI Intent API. Aria never executes OS actions directly.

---

## 🚀 Unified CLI Usage

Aria provides a unified command-line tool `aria` (or `python -m aria`):

```bash
# Run a voice pipeline turn (simulated in CI / testing)
aria run --mode aria --query "Hello Aria, what is your status?"
aria run --mode jarvis --query "System diagnostic report."

# Run the real-time latency and throughput benchmark harness
aria benchmark

# Manage user preferences and system settings (stored in SQLite)
aria config --set voice_id "aria-v1-warm"
aria config --get default_mode

# Database memory management & privacy controls
aria memory --stats
aria memory --purge    # Instant privacy purge of all history and facts

# Start the visual overlay WebSocket server
aria overlay --port 8765
```

---

## 📁 Repository Structure

```
.
├── 01-Aria-Vision-Concept.md          # Core vision (LOCKED)
├── 02-Aria-Architecture-and-Build-Guide.md # Architecture guide (LOCKED)
├── 03-Aria-UI-UX-Spec.md              # UI/UX specification (LOCKED)
├── 04-Mandatory-Pipeline-Architecture.md # Technical pipeline contract
├── aria/                              # Core Python package
│   ├── cli.py                         # Unified CLI entry point
│   ├── core/
│   │   ├── audio/                     # Audio capture, analysis, and playback bridges
│   │   ├── config.py                  # User preferences and system configuration
│   │   ├── intent/                    # Directioner AI Intent API, schemas & confirmation
│   │   ├── llm/                       # Groq LPU reasoning client & personality matrices
│   │   ├── media/                     # Media playback controller & beat synchronizer
│   │   ├── memory/                    # SQLite session & bounded long-term storage
│   │   ├── pipeline/                  # Canonical pipeline orchestrator & event bus
│   │   ├── stt/                       # smallest.ai streaming STT
│   │   ├── tts/                       # smallest.ai streaming TTS
│   │   ├── vad/                       # Silero VAD wrapper
│   │   ├── vision/                    # Screen awareness & vision tools
│   │   └── wake/                      # openWakeWord dual-model detector
│   └── visual/
│       ├── aria_mode/                 # Aria soft orb WebGL/Canvas renderer
│       ├── canvas/                    # Floating canvas panels & adaptive layouts
│       ├── jarvis_mode/               # Jarvis Arc-Reactor HUD WebGL/Canvas renderer
│       └── overlay/                   # Compositor bridge, WebSocket server & HTML app
├── tests/                             # Unit, integration, & benchmark tests
├── .github/
│   ├── workflows/                     # GitHub Actions CI (lint, typecheck, test, benchmark)
│   └── ISSUE_TEMPLATE/                # Structured issue templates
└── pyproject.toml
```

---

## 🛠️ CI & Development Workflow

All testing, building, and validation is automated in GitHub Actions.

```bash
# Run linters and formatting
ruff check .
ruff format --check .

# Run strict type checking
mypy aria tests

# Run test suite with code coverage
pytest -v --cov=aria
```

---

## 📜 License

Licensed under the [Apache License, Version 2.0](LICENSE).
