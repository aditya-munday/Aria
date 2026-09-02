# Issue #2: Phase 1 — Core Voice Pipeline Skeleton

**Status:** PLANNED  
**Labels:** `phase-1`, `core-pipeline`, `architecture`  
**Assignee:** Aria Lead Engineer Agent  

---

## Objective
Implement the modular core voice pipeline according to `04-Mandatory-Pipeline-Architecture.md`:
`openWakeWord (dual models) → Silero VAD → smallest.ai STT → Grok (xAI) → smallest.ai TTS → Audio Analysis`

## Acceptance Criteria
- [ ] **Wake Word Manager (`aria/core/wake/`):**
  - Dual wake word detection ("Aria" vs "Jarvis")
  - Clean abstraction supporting both local openWakeWord engine and CI test adapter
  - Mode transition signal emitter
- [ ] **Silero VAD Wrapper (`aria/core/vad/`):**
  - Frame-based voice activity detection
  - Speech start and end-of-utterance detection
- [ ] **Streaming STT Client (`aria/core/stt/`):**
  - smallest.ai websocket streaming STT client interface
  - Partial and final transcript event generation
  - Mock STT engine for zero-network CI testing
- [ ] **Reasoning & Personality Matrix (`aria/core/llm/`):**
  - Grok (xAI) client interface with tool/function calling
  - Distinct personality matrices for Aria Mode (soft, concise, elegant) vs Jarvis Mode (authoritative, dense, technical)
  - `delegate_to_directioner_ai` tool specification
- [ ] **Streaming TTS Client (`aria/core/tts/`):**
  - smallest.ai streaming TTS client interface
  - Chunked audio byte streaming
  - Mock TTS engine for zero-network CI testing
- [ ] **Audio Analysis (`aria/core/audio/`):**
  - Real-time amplitude, spectral energy, and beat tracking to drive visual overlay state
- [ ] **Database & Memory Layer (`aria/core/memory/`):**
  - SQLite persistent store for sessions, conversations, and long-term user preferences
  - Explicit growth and eviction policy
- [ ] **Pipeline Orchestrator (`aria/core/pipeline/`):**
  - State machine with IDLE, LISTENING, THINKING, SPEAKING, DELEGATING, CONFIRMATION_REQUIRED, MEDIA_REACTIVE
  - End-to-end event bus and pipeline loop
