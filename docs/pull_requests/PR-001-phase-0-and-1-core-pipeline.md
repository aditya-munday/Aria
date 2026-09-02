# PR #1: Phase 0 & Phase 1 — Core Voice Pipeline Skeleton, Groq Reasoning, Memory, and CI Harness

## Summary of Changes
Implements the foundation and canonical voice pipeline for Aria v0.1 conforming strictly to `04-Mandatory-Pipeline-Architecture.md`:
- **Repository Hygiene & CI:** `.gitignore`, Apache-2.0 `LICENSE`, `pyproject.toml`, `README.md`, GitHub Actions workflow (`.github/workflows/ci.yml`), issue templates, and PR template.
- **Canonical Pipeline Modules:**
  1. `openWakeWord` dual-model detection ("Aria" / "Jarvis") with mode emission.
  2. `Silero VAD` wrapper with silence tracking and end-of-utterance calculation.
  3. `smallest.ai STT` streaming WebSocket client with partial & final transcript parsing.
  4. `Groq` reasoning client (powered by LPU low TTFT) with dual personality matrices (Aria Mode vs Jarvis Mode) and tool calling.
  5. `smallest.ai TTS` streaming speech generation.
  6. `AudioAnalyzer` computing real-time RMS amplitude, spectral energy, pitch proxy, and dynamic beat detection.
  7. `PipelineOrchestrator` coordinating the canonical async loop across all states.
- **Memory & Database Layer:** SQLite persistent store with explicit FIFO history eviction (bounded at 5,000 interactions), LRU fact bounding (1,000 items), and instant privacy wipe.
- **Directioner AI Safety Boundary:** Strict Intent API client with `delegate_to_directioner_ai` tool; zero local OS execution.
- **Visual Overlay Foundation:** State machine handling 7 visual states, mode switch transformations (600-800ms), and audio reactive scaling.
- **Verification Harness:** 26 automated tests covering unit tests, integration tests, and latency benchmarks.

---

## 🔍 Component Verification Matrix (REAL vs MOCKED)

| Component | Status (`REAL` / `MOCKED`) | Details / Behavior in CI |
| :--- | :--- | :--- |
| **Wake Word (openWakeWord)** | `MOCKED` in CI / `REAL` interface ready | `OpenWakeWordDetector` wraps local ONNX runtime; `MockWakeWordDetector` injects synthetic wake detections during CI tests. |
| **VAD (Silero VAD)** | `MOCKED` in CI / `REAL` interface ready | `SileroVADDetector` wraps PyTorch/ONNX hub model; `MockVADDetector` verifies frame accumulation and end-of-utterance state logic in CI. |
| **STT (smallest.ai)** | `MOCKED` in CI / `REAL` interface ready | `SmallestStreamingSTT` implements WebSocket protocol; `MockStreamingSTT` emits streaming partials and finals in CI. |
| **Reasoning / LLM (Groq)** | `MOCKED` in CI / `REAL` interface ready | `GroqClient` streams OpenAI-compatible completions and function calls; `MockLLMClient` exercises streaming token chunks and tool call dispatching in CI. |
| **TTS (smallest.ai)** | `MOCKED` in CI / `REAL` interface ready | `SmallestStreamingTTS` implements chunked streaming audio receiver; `MockStreamingTTS` yields synthetic PCM chunks with TTFB recording in CI. |
| **Audio Analysis** | `REAL` in CI | `AudioAnalyzer` computes real numpy-based RMS amplitude, spectral energy, zero-crossing pitch proxy, and dynamic energy variance beat detection. |
| **Intent API (Directioner AI)**| `REAL` in CI | `DirectionerAIClient` validates Pydantic schemas, enforces risk tier confirmations, and records execution audit history without calling local OS commands. |
| **Memory & Storage** | `REAL` in CI | `LongTermMemory` executes real SQLite queries, WAL pragmas, FIFO history trimming, and LRU fact bounding in memory/disk. |

---

## ⏱️ Latency & Performance Metrics
- **AudioAnalyzer Frame Compute Latency:** `0.0076 ms` average per 512-sample frame (measured via `test_audio_analyzer_frame_latency` in CI harness; requirement: <1.0 ms).
- **Synthetic End-to-End Pipeline Turn Latency:** `31.42 ms` end-to-end (measured via `test_end_to_end_mock_pipeline_turn_latency` in CI harness; requirement: <500 ms).
- **Live Network STT / Groq / TTS Latency:** *not yet measurable in CI* (requires production API keys and network access).

---

## ✅ Itemized Verification Checklist

- [x] **Linter & Formatting:** `ruff check .` and `ruff format --check .` passing with 0 errors across all 74 files.
- [x] **Type Checking:** `mypy aria tests` passing with 0 issues in 55 source files under strict settings.
- [x] **Unit & Integration Tests:** 26/26 tests passing in `pytest -v --cov=aria` (76% overall test coverage across modules).
- [x] **Pipeline Order Compliance:** Canonical order in `04-Mandatory-Pipeline-Architecture.md` (Wake -> VAD -> STT -> Groq -> TTS -> Audio Analysis) strictly enforced in `PipelineOrchestrator.run_voice_turn`.
- [x] **Directioner AI Boundary:** Zero OS-level or shell calls in Aria codebase; all system actions route strictly via `delegate_to_directioner_ai`.
- [x] **Memory Policy Stated:** Explicit eviction/retention/growth policy documented in `docs/design_decisions/DD-002-long-term-memory-eviction.md` and enforced in `LongTermMemory`.
- [x] **Confirmation UX:** Documented with options and tradeoffs in `docs/design_decisions/DD-001-confirmation-ux.md`.

---

## Known Gaps & Future Work
- Visual rendering shaders / WebGL canvas implementation (scheduled for Phase 2).
- Electron / Wayland transparent window compositor harness.
- Live end-to-end testing against smallest.ai and Groq staging endpoints with secret keys in CI.
