# Aria — Directioner Voice Assistant
## Ultimate Vision, Concept & Living Spec
**Project:** Aria  
**Codename Status:** Living Constitution  
**Version:** 3.0 — Ultra Expanded  
**Track:** Parallel to Directioner-OS Core  
**Primary Identity:** Dual-Mode Voice Presence (Aria Mode + Jarvis Mode)

> Aria is not an assistant that lives inside an app.  
> Aria *is* the operating system’s face, voice, and presence.

---

## 0. Dual-Mode Identity — The Defining Principle

Aria is deliberately designed as **two distinct experiences** controlled by the wake word itself.

| Aspect                    | Aria Mode (Default)                          | Jarvis Mode                                      |
|---------------------------|----------------------------------------------|--------------------------------------------------|
| **Wake Word**             | “Hey Aria” / “Aria”                          | “Jarvis” / “Hey Jarvis”                          |
| **Personality**           | Warm, minimal, elegant, approachable         | Authoritative, precise, cinematic, hyper-capable |
| **Visual Language**       | Soft luminous orb / edge-glow / subtle waveform | Full holographic HUD, Arc-Reactor core, particle fields, multi-panel Canvas |
| **Capability Surface**    | Fast conversational + light utility          | Full system orchestration + spatial awareness + proactive intelligence |
| **Tone of Voice**         | Conversational, concise, friendly            | Formal, confident, slightly dry wit, highly informative |
| **Default Density**       | Minimal                                      | Information-dense                                |

Saying **“Jarvis”** is not merely activation — it is a **mode transformation**.  
The visual presence, personality matrix, response style, panel density, and available surface area all shift instantly.

This dual-mode architecture solves a real product problem:
- Everyday users get a beautiful, non-intimidating experience.
- Power users, developers, and enthusiasts get a true Iron-Man-class command interface on demand.

Both modes share the exact same underlying stack, memory system, and the inviolable delegation boundary to Directioner AI.

---

## 1. Architectural Boundary (Sacred Rule)

This is the single most important architectural decision in the entire project:

- **Aria owns**:  
  Wake detection, full voice pipeline, personality, visual overlay, Canvas Mode, media playback, session & long-term memory, intent formation, and user-facing narration.

- **Directioner AI (the AI Engineer) owns**:  
  Every actual system action — files, packages, services, kernel, settings, network, security, policy, blast-radius scoring, and execution.

- **The only connection** is a narrow, versioned, well-documented Intent API:
  1. Aria forms a natural-language or structured intent + rich context.
  2. Directioner AI’s existing pipeline (IntentParser → PlanDraftValidator → PolicyEngine → Reviewer) processes it.
  3. Aria receives a plan, status, risk score, or final result and narrates it back to the user.

**Aria never executes system capabilities itself.**  
This boundary is what makes “build it separately and fast” actually safe rather than reckless.  
The Assistant track never needs to touch policy engines, capability daemons, or safety review.  
The Directioner AI track never needs to think about wake words, animation, or TTS.

---

## 2. What Aria Is (and Explicitly Is Not)

### Is
- A fast, always-listening (opt-in), highly responsive conversational and visual layer that lives at the compositor / system level.
- The living face and voice of Directioner-OS.
- Capable of pure conversation, information retrieval, media control, and multi-panel visual composition without ever touching the OS.
- Capable of triggering real system changes *only* by delegating to Directioner AI.

### Is Not
- A traditional application with a window you “open”.
- An independent agent that can bypass Directioner AI’s safety pipeline.
- A replacement for Directioner AI’s reasoning about system risk.

The only conventional app is a lightweight **Settings & Management Companion** for:
- Wake-word sensitivity & custom phrases
- Voice selection / cloning
- Privacy controls & microphone history
- Overlay appearance & theme
- Permissions & multi-user profiles
- Usage analytics (local)

---

## 3. Activation Paths

1. **Wake Word** (openWakeWord + Silero VAD)  
   - “Hey Aria” / “Aria” → Aria Mode  
   - “Jarvis” / “Hey Jarvis” → Jarvis Mode (full transformation sequence)

2. **Keyboard Shortcut** (configurable, recommended Super + Space or Super + J)

3. **Gesture / Hot Corner** (phase 2)

4. **Ambient Presence Indicator** (tiny always-visible optional widget — tap to activate)

5. **Push-to-Talk** hardware key (future)

All activation paths feed the identical pipeline; only the presentation layer and personality matrix differ.

---

## 4. The Visual Presence — Living Compositor Overlay

Aria is rendered as a fully transparent, always-on-top overlay directly on the compositor.  
It never creates a traditional window. It never pauses or obscures the application underneath unless Canvas Mode is deliberately dense.

### 4.1 Aria Mode Visual Language (Siri-class)
- Soft luminous orb or adaptive edge-glow that reacts to voice amplitude and pitch.
- Extremely minimal ambient presence when idle.
- Distinct, unmistakable states:
  - Idle / Dormant — nearly invisible
  - Listening — gentle “leaning in” pulse
  - Thinking — soft orbital motion / searching particles
  - Speaking — true voice-reactive glow
  - Delegating — subtle system-working indicator
  - Confirmation Required — high-contrast soft pulse

Color and intensity adapt to system theme (light/dark) and time of day.

### 4.2 Jarvis Mode Visual Language (Ultimate)
When the user speaks the word “Jarvis”, a short cinematic transformation occurs:

- Central **Arc-Reactor Core** materializes (multi-layer rotating rings + particle field + energy core).
- Connecting energy lines / scan-line trails can appear.
- Full holographic framing language activates.
- State machine becomes richer and more cinematic:
  - Idle — faint ambient particle drift
  - Listening — expanding concentric rings + attentive lean
  - Thinking / Processing — data streams flowing into the core, searching particle fields
  - Speaking — high-fidelity voice-reactive (amplitude + pitch + rhythm + formant influence)
  - Delegating to Directioner AI — distinct amber / data-transfer animation so the user *sees* that a real system action is underway
  - Alert / Confirmation — unmistakable high-contrast, authoritative state
  - Media Mode — true beat-synced particle field driven by real-time audio analysis
  - Canvas Mode Active — the core becomes the gravitational center of the multi-panel layout

All motion is driven by real-time audio analysis, never pre-baked loops.

---

## 5. Canvas Mode — Dynamic Multi-Window Workspace

For any information-dense request, Aria does not merely speak an answer — it **composes a live visual workspace**.

- Multiple floating, borderless, glassmorphic widget panels appear around the screen.
- Each panel is purpose-built (live news feed, market chart, weather, calendar, system status, article card, code snippet, etc.).
- Visual linking: subtle energy lines, shared particle trails, or synchronized fade-in make it clear that “Aria built this for you.”
- Adaptive layout engine:
  - One clear panel for simple answers
  - Fan / grid / radial / edge-docked arrangements for multi-part answers
- Ephemeral by default (auto-dismiss after timeout or on “dismiss these”).
- Any individual panel can be pinned permanently.
- Voice or drag re-arrangement supported (“move the weather panel to the left”, “make the chart larger”).
- In Jarvis Mode the panels gain holographic framing, scan lines, deeper data density, and more aggressive information design.

---

## 6. Media Playback & Reactive Visuals

- Built-in lightweight media player for zero-latency “play [song / video]”.
- When audio is playing, the visual identity switches into **true beat-reactive mode** driven by real-time frequency and amplitude analysis.
- Explicit escalation path: “play it on YouTube / Spotify / VLC” hands off to the preferred external application.
- Video can appear as floating Canvas panels.
- Future: lyrics overlay, waveform scrubbing, and spatial audio visualization.

---

## 7. Speed & Responsiveness — Core Product Requirement

A Jarvis-style assistant that lags destroys the illusion.  
Latency is not polish. Latency *is* the product.

**Current chosen stack (optimized for sub-second feel):**
- openWakeWord → local, instant wake detection
- Silero VAD → precise end-of-utterance detection (prevents cutting off or waiting too long)
- smallest.ai → low-latency streaming STT
- Groq → industry-leading low-latency inference
- smallest.ai → streaming TTS (first audio chunk as early as possible)

**Design implications:**
- The “Thinking” visual state is the primary latency sponge. Even when the model takes 400–800 ms, the interface never freezes.
- Streaming TTS starts speaking while the rest of the answer is still being generated.
- Aggressive barge-in support: the user can interrupt mid-sentence and Aria stops cleanly.
- Speculative caching of common intents and visual assets.
- Local-first design wherever possible.

Target experience: the assistant should feel *alive* and *instant*, not “smart but slow.”

---

## 8. Delegation Boundary & Voice Confirmation UX (Critical)

When a request implies system risk (“turn on dark mode”, “install X”, “restart the network service”, “delete these files”), Aria:

1. Visibly switches into the **Delegating** state.
2. Sends the intent + full context to Directioner AI’s existing hardened pipeline.
3. Receives a plan, risk score, and confirmation requirement.
4. Narrates a concise risk summary to the user.
5. Enters the distinct **Alert / Confirmation** visual state.
6. Requires clear verbal confirmation (“Yes, proceed”, “Confirm”, “Do it”) or a secondary gesture.
7. Timeout or silence = automatic cancel.

The confirmation UX must be designed deliberately. A terminal-style y/N prompt does not work in a voice + visual interface. This is a focused design problem that must be solved before the delegation link is considered complete.

The user must always be able to *see* the exact moment they cross from conversation into authorizing a real system change.

---

## 9. Ultra Feature Set

### Intelligence & Conversation
- Session-level contextual memory with perfect pronoun and reference resolution
- Long-term personalization (preferences, common workflows, voice, visual density)
- Multi-turn, fully interruptible conversation
- Screen-aware context (opt-in) — “summarize this article”, “what does this error mean?”
- Proactive, non-nagging suggestions surfaced through the ambient presence indicator
- Emotional tone adaptation based on time of day and context

### Visual & Spatial
- Adaptive theming that follows system theme, time of day, and media mood
- Ambient presence indicator (tiny, optional, always-visible)
- Do-not-disturb / Focus / Fullscreen / Game awareness
- Transparent, unmissable trust indicators for microphone state
- Future spatial / AR-ready layout engine

### Voice & Identity
- Multiple high-quality system voices
- User voice cloning (opt-in, local)
- Custom wake phrases
- Multi-user voice recognition with per-user personalization and permission profiles
- Voice emotion detection (future)

### System & Productivity (via Directioner AI only)
- Full OS control through the existing safe pipeline
- Live system monitoring panels (CPU, memory, network, temperature, processes)
- Cross-device continuity on trusted local network
- Workflow macros and scene triggers (“start my coding session”, “evening wind-down”, “presentation mode”)
- Clipboard and selection awareness

### Media & Information
- Instant media with true beat-reactive visuals
- Live multi-panel briefings
- Smart window and panel management
- Article / document summarization with Canvas cards

### Trust, Privacy & Safety
- Fully local wake-word + VAD path
- Persistent visual indicator of listening state
- All system actions inherit Directioner AI’s blast-radius scoring, Reviewer vetoes, and adversarial resistance
- Local usage history with easy export / wipe
- Explicit privacy controls in the companion Settings app

---

## 10. Explicit Non-Goals (v1 Scope Control)

- No shadow execution path that bypasses Directioner AI
- Continuous full-screen vision is an extension, not a v1 requirement
- Multi-user voice recognition and cross-device hand-off are phase-2
- No mandatory always-on cloud dependency for the core loop
- No permanent desktop takeover or forced dashboard

---

## 11. Design Principles (North Stars)

1. **Latency is the product.** Anything that feels slow breaks the magic.
2. **The visual language must always tell the truth** about the current state (listening, thinking, speaking, delegating, waiting for confirmation).
3. **Aria Mode is beautiful and approachable. Jarvis Mode is powerful and cinematic.** Both must feel native to Directioner-OS.
4. **Never invent a second execution path.** Safety is inherited, never reimplemented.
5. **Transparency builds trust.** The user must always know when the microphone is live and when a real system action is about to happen.
6. **Ephemeral by default, persistent on request.**
7. **Personality is a feature.** The dual-mode shift must feel intentional and delightful, not jarring.

---

## 12. Suggested Build Order (High-Level)

1. Core voice loop (dual wake words + STT + Groq + streaming TTS) — text-only, prove latency.
2. Aria Mode visual identity + complete state machine.
3. Jarvis Mode transformation sequence + Arc-Reactor core + richer particle systems.
4. Delegation link to Directioner AI + deliberate voice confirmation UX design.
5. Media playback + true beat-reactive visuals.
6. Canvas Mode (multi-panel generation, linking, pinning, adaptive layout).
7. Personality matrix, session memory, and long-term personalization.
8. Advanced features (screen awareness, multi-user, proactive suggestions, cross-device).

---

This document is the living constitution of Aria.  
It is deliberately ambitious because the parallel-track model and the already-hardened Directioner AI pipeline make ambition safe.

Treat every section as open to refinement as implementation reveals reality — but never dilute the dual-mode identity or the architectural boundary.

**Aria is the face.  
Directioner AI is the mind.  
Together they become the most advanced personal computing presence yet designed.**
