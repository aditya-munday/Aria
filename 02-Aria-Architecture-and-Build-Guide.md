# Aria — Architecture & Build Guide
**Companion Document to the Vision Spec**  
**Version:** 3.0  
**Audience:** Engineers building the Aria track

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User (Microphone / Keyboard)            │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Aria Runtime (Compositor Overlay)        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ openWakeWord │→ │ Silero VAD   │→ │ Streaming STT    │  │
│  │ (dual models)│  │              │  │ (smallest.ai)    │  │
│  └──────────────┘  └──────────────┘  └────────┬─────────┘  │
│                                               │             │
│  ┌────────────────────────────────────────────▼──────────┐  │
│  │              Intent & Personality Engine              │  │
│  │  - Mode detection (Aria vs Jarvis)                    │  │
│  │  - Session memory                                     │  │
│  │  - Context assembly                                   │  │
│  │  - Decision: handle locally or delegate               │  │
│  └────────────┬───────────────────────────────┬──────────┘  │
│               │                               │             │
│               ▼                               ▼             │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │ Local Handlers     │          │ Directioner AI       │  │
│  │ - Conversation     │          │ Intent API           │  │
│  │ - Media control    │          │ (narrow, versioned)  │  │
│  │ - Canvas composition│         └──────────┬───────────┘  │
│  │ - Visual state mgmt│                     │             │
│  └────────┬───────────┘                     │             │
│           │                                 │             │
│           ▼                                 ▼             │
│  ┌────────────────────┐          ┌──────────────────────┐  │
│  │ Streaming TTS      │          │ Directioner AI       │  │
│  │ + Audio Analysis   │          │ Pipeline             │  │
│  │ (for reactivity)   │          │ (Plan → Policy →     │  │
│  └────────┬───────────┘          │  Reviewer → Result)  │  │
│           │                      └──────────┬───────────┘  │
│           │                                 │             │
│           ▼                                 ▼             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Visual & Audio Output Layer             │  │
│  │  - Compositor Overlay (orb / Arc-Reactor / panels)   │  │
│  │  - State machine driven animations                   │  │
│  │  - Beat / voice reactive particle systems            │  │
│  │  - Canvas panel manager                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Technology Stack (Recommended)

| Layer                  | Technology                          | Reason |
|------------------------|-------------------------------------|--------|
| Wake Word              | openWakeWord (custom dual models)   | Local, fast, open, trainable |
| Voice Activity         | Silero VAD                          | Excellent accuracy + low latency |
| Speech-to-Text         | smallest.ai (or WhisperLive / faster-whisper) | Streaming, low latency |
| Reasoning / LLM        | Groq (Llama 3.3 70B or equivalent)  | Industry-leading TTFT |
| Text-to-Speech         | smallest.ai streaming TTS           | Low latency first chunk |
| Audio Analysis         | Web Audio API / essentia / aubio    | Real-time amplitude, pitch, beat |
| Overlay Rendering      | Wayland / X11 compositor layer or Electron + transparent window + Canvas/WebGL / Three.js | Always-on-top, transparent |
| Particle / HUD         | Three.js or custom WebGL / Skia     | High performance particle systems |
| Panel System           | Custom floating windows managed by compositor or Electron BrowserViews | Borderless, linked, ephemeral |
| Local Storage          | SQLite + encrypted key-value        | Session + long-term memory |
| IPC / Intent API       | gRPC or well-defined HTTP + JSON schema | Clean boundary with Directioner AI |

---

## 3. Recommended Project Structure

```
aria/
├── core/
│   ├── wake/
│   │   ├── openwakeword_manager.py
│   │   └── dual_model_config.yaml
│   ├── vad/
│   │   └── silero_wrapper.py
│   ├── stt/
│   │   └── streaming_stt.py
│   ├── llm/
│   │   ├── groq_client.py
│   │   └── personality_matrix.py
│   ├── tts/
│   │   └── streaming_tts.py
│   ├── audio/
│   │   ├── analyzer.py          # amplitude, pitch, beat detection
│   │   └── player.py
│   ├── memory/
│   │   ├── session.py
│   │   └── long_term.py
│   └── intent/
│       ├── classifier.py
│       └── directioner_client.py
├── visual/
│   ├── overlay/
│   │   ├── compositor_bridge.py
│   │   └── state_machine.py
│   ├── aria_mode/
│   │   └── soft_orb.js / .ts
│   ├── jarvis_mode/
│   │   ├── arc_reactor.js
│   │   └── particle_system.js
│   ├── canvas/
│   │   ├── panel_manager.py
│   │   └── layout_engine.py
│   └── themes/
├── ui/
│   └── settings-companion/      # lightweight Electron or native app
├── proto/                       # Intent API definitions
├── tests/
├── docs/
└── scripts/
    ├── train_wake_words.sh
    └── latency_benchmark.py
```

---

## 4. Build Phases (Detailed)

### Phase 0 — Foundation (1–2 weeks)
- Project scaffolding
- Dual wake-word models trained / configured (“Aria” and “Jarvis”)
- Silero VAD integrated
- Basic microphone capture pipeline
- Latency measurement harness

**Exit criteria:** “Hey Aria” and “Jarvis” reliably detected with low false positives.

### Phase 1 — Core Voice Loop (2–3 weeks)
- Streaming STT → Groq → Streaming TTS end-to-end
- Text-only responses
- Basic barge-in
- Latency under 800–1000 ms end-to-end on target hardware

**Exit criteria:** Natural conversation feels responsive. User can interrupt cleanly.

### Phase 2 — Aria Mode Visuals (2 weeks)
- Transparent always-on-top overlay
- Soft orb / edge-glow implementation
- Complete state machine (Idle, Listening, Thinking, Speaking, Delegating, Confirm)
- Voice-reactive animation driven by real audio analysis

**Exit criteria:** Visual state always matches actual pipeline state. Feels alive.

### Phase 3 — Jarvis Mode Transformation (2–3 weeks)
- Arc-Reactor core + multi-layer rings
- Particle systems
- Cinematic mode-switch animation when “Jarvis” is detected
- Richer state visuals and holographic framing

**Exit criteria:** Mode switch feels intentional and delightful. Jarvis Mode is clearly more powerful visually.

### Phase 4 — Delegation Link (Critical, 2–3 weeks)
- Define and implement the narrow Intent API (protobuf or JSON schema)
- Wire to existing Directioner AI pipeline
- Design and implement voice + visual confirmation UX
- Risk summary narration
- Timeout / cancel behavior

**Exit criteria:** Every system action goes through Directioner AI. Confirmation is clear and safe.

### Phase 5 — Media + Reactivity (1–2 weeks)
- Built-in audio/video player
- Real-time beat detection
- Switch visual system into beat-reactive mode
- Platform hand-off commands

### Phase 6 — Canvas Mode (3–4 weeks)
- Floating panel system
- Adaptive layout engine
- Visual linking (energy lines / particle trails)
- Pin / dismiss / rearrange by voice
- Multi-panel composition for complex queries

### Phase 7 — Memory, Personality & Polish
- Session memory with reference resolution
- Long-term personalization store
- Personality matrix differences between modes
- Ambient presence indicator
- Settings companion app
- Trust indicators and privacy controls

### Phase 8 — Advanced (Post-v1)
- Screen awareness
- Multi-user voice profiles
- Cross-device continuity
- Proactive suggestions
- Spatial / AR extensions

---

## 5. Key Implementation Notes

### Dual Wake Word Handling
Train or fine-tune two separate openWakeWord models.  
On detection:
- “Aria” family → set `current_mode = "aria"`
- “Jarvis” family → set `current_mode = "jarvis"` and trigger transformation sequence

Both models can run in parallel on the same audio stream with minimal overhead.

### State Machine
Every visual and audio decision must be driven by a single source of truth state machine.  
Never let the visual layer invent state independently.

### Intent Classification
Before calling Directioner AI, classify whether the request is:
- Pure conversation / information → handle locally
- Media control → handle locally
- System action → must delegate
- Ambiguous → ask clarifying question or default to safe path

### Confirmation UX Requirements
- Visual state change must be unmistakable
- Spoken risk summary must be concise and honest
- Confirmation phrase should be configurable but clear
- Always provide an easy cancel path
- Log every confirmation event for auditability

### Latency Budget (Target)
- Wake detection: < 150 ms
- VAD end-of-speech: < 200 ms
- STT first partial: < 300 ms
- LLM first token: < 200–400 ms (Groq)
- TTS first audio chunk: < 200 ms
- Total perceived: ideally under 800–1000 ms for simple turns

---

## 6. Testing Strategy

- Latency benchmarks on every PR
- False wake / missed wake rate tracking
- Barge-in accuracy tests
- Mode switch reliability
- Confirmation flow adversarial testing
- Visual state correctness (does the animation always match reality?)
- Long-session memory consistency
- Privacy: verify no audio leaves the machine unless explicitly allowed

---

## 7. Security & Privacy Requirements

- Microphone access is opt-in and clearly indicated
- Wake-word and VAD run fully locally
- No raw audio leaves the device by default
- All system actions inherit Directioner AI’s existing safety guarantees
- Settings companion must make it trivial to disable listening, wipe history, and review permissions

---

This guide is the practical companion to the Vision document.  
Follow the phases in order. Do not skip the confirmation UX design.  
Latency and the dual-mode identity are non-negotiable product requirements.

Build the face carefully. The mind already exists.
