# Aria — Mandatory Runtime Pipeline Architecture
**Status:** Binding for all implementation  
**Note:** This document does **not** replace the three locked vision documents. It only defines the concrete technical pipeline that must be followed.

---

## 1. Canonical Pipeline Order (Non-Negotiable)

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
Visual Overlay + Canvas + Advanced Vision Control (phase 2+)
```

Any deviation from this order requires an explicit architecture decision record and a GitHub issue.

---

## 2. Component Responsibilities

### 1. openWakeWord
- Two separate models running on the same audio stream
- “Aria” family → set mode = `aria`
- “Jarvis” family → set mode = `jarvis` + trigger transformation
- Fully local

### 2. Silero VAD
- Determines when the user has finished speaking
- Prevents premature cut-off and excessive waiting
- Feeds clean speech segments to STT

### 3. smallest.ai STT
- Streaming speech-to-text
- Low latency partials preferred
- Output goes to the Intent & Personality layer

### 4. Groq (Reasoning & LLM)
- Primary reasoning engine (Llama-3.3-70B on Groq LPU inference for ultra-low TTFT)
- Receives:
  - Current mode (Aria / Jarvis)
  - System prompt (different personality matrix per mode)
  - Session memory + long-term memory from database
  - Optional screen / vision context (future)
  - Available tools (including Directioner AI Intent API)
- Must support tool calling / function calling
- Must never execute OS actions itself — only emit intents

### 5. Database Layer
- Session memory (short-term context, references, open panels)
- Long-term memory (user preferences, voice, common workflows)
- Conversation history (privacy-controlled)
- Recommended: SQLite for local + optional remote sync later

### 6. smallest.ai TTS
- Streaming text-to-speech
- First audio chunk as early as possible
- Audio is also fed to the real-time analysis engine for visual reactivity

### 7. Advanced Vision Control (Phase 2+)
- Architecture must already expose a clean interface for:
  - Screen capture / window context
  - Vision model calls
  - “What is on my screen?” style queries
- Implementation can come later; the pipeline and tool interface must be ready

---

## 3. Dual-Mode Personality via System Prompts

Groq must receive different system prompts depending on the active mode:

- **Aria Mode**: warm, concise, elegant, helpful, lower information density
- **Jarvis Mode**: precise, authoritative, slightly formal, higher information density, willing to surface system status and alternatives

The mode is set at wake-word detection and remains stable for the session unless the user explicitly switches.

---

## 4. Directioner AI Boundary (Still Sacred)

Even with the new pipeline, Aria **never** executes system actions.  
All OS-touching requests are turned into intents and sent through the existing Directioner AI pipeline.  
Groq may call a `delegate_to_directioner_ai` tool; it may not call shell, filesystem, or package tools directly.

---

## 5. CI / Execution Constraint

- No component may assume it can run a long-lived process on a developer laptop.
- All integration tests, latency measurements, and end-to-end checks must be expressible as GitHub Actions jobs.
- Local `git` + `gh` + file editing only.

---

This document is the concrete technical contract.  
All new code must conform to it.
