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
[4] Grok (xAI)            ← system prompts + tools + database memory
    ↓
[5] smallest.ai TTS       ← streaming audio out
    ↓
[6] Audio Analysis        ← amplitude / pitch / beat → drives visuals
    ↓
Visual Overlay + Canvas + Advanced Vision Control (phase 2+)
```

All system actions **must** delegate to the Directioner AI Intent API. Aria never executes OS actions directly.

---

## 📁 Repository Structure

```
.
├── 01-Aria-Vision-Concept.md          # Core vision (LOCKED)
├── 02-Aria-Architecture-and-Build-Guide.md # Architecture guide (LOCKED)
├── 03-Aria-UI-UX-Spec.md              # UI/UX specification (LOCKED)
├── 04-Mandatory-Pipeline-Architecture.md # Technical pipeline contract
├── aria/                              # Core Python implementation
│   ├── core/
│   │   ├── audio/                     # Audio capture, analysis, playback
│   │   ├── intent/                    # Directioner AI Intent API boundary
│   │   ├── llm/                       # Grok reasoning & personality matrix
│   │   ├── memory/                    # SQLite session & long-term memory
│   │   ├── pipeline/                  # Canonical pipeline orchestrator & events
│   │   ├── stt/                       # smallest.ai streaming STT
│   │   ├── tts/                       # smallest.ai streaming TTS
│   │   ├── vad/                       # Silero VAD wrapper
│   │   └── wake/                      # openWakeWord dual-model detector
│   └── visual/
│       └── overlay/                   # Compositor bridge & state machine
├── tests/                             # Unit, integration, & benchmark tests
├── .github/
│   ├── workflows/                     # GitHub Actions CI (lint, typecheck, test, benchmark)
│   └── ISSUE_TEMPLATE/                # Structured issue templates
└── pyproject.toml
```

---

## 🛠️ CI & Development Workflow

All testing, building, and validation is automated in GitHub Actions.

### Quick Commands

```bash
# Run linters
ruff check .

# Run type checker
mypy aria tests

# Run test suite
pytest -v
```

---

## 📜 License

Licensed under the [Apache License, Version 2.0](LICENSE).
