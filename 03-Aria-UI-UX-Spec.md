# Aria — UI / UX Specification
**Companion Document**  
**Version:** 3.0  
**Focus:** Visual language, interaction, motion, and trust design

---

## 1. Design Philosophy

Aria must feel like a **living presence**, not a tool that opens and closes.

- **Aria Mode** = elegant, calm, minimal, approachable (modern Siri / Apple Intelligence feeling)
- **Jarvis Mode** = powerful, cinematic, information-dense, slightly formal (Iron Man HUD feeling)

The transition between the two modes is itself a designed moment — short, satisfying, and intentional.

Core principles:
1. State is always visible and truthful.
2. Motion is driven by real audio, never fake loops.
3. Density scales with mode and request complexity.
4. Trust indicators are permanent and unmissable.
5. Ephemeral by default.

---

## 2. Visual Identity System

### 2.1 Color & Material Language

**Aria Mode**
- Soft luminous gradients (cool blues, soft violets, warm whites)
- High transparency, gentle bloom
- Thin, elegant strokes
- Adaptive to system light/dark theme

**Jarvis Mode**
- Deeper, richer palette (electric cyan, deep blue, amber accents for alerts)
- Glassmorphic + holographic framing
- Energy lines, scan lines, subtle noise/grain
- Stronger contrast and higher information density

Both modes respect the system theme while maintaining their own identity.

### 2.2 Core Visual Elements

| Element              | Aria Mode                          | Jarvis Mode                              |
|----------------------|------------------------------------|------------------------------------------|
| Primary Presence     | Soft orb or edge-glow              | Multi-layer Arc-Reactor core             |
| Secondary Motion     | Gentle pulse / orbital particles   | Particle fields + rotating rings         |
| Connecting Lines     | Rare / subtle                      | Energy trails linking panels to core     |
| Panel Style          | Clean glass cards                  | Holographic framed panels with scan lines|
| Typography           | Clean sans, medium weight          | Slightly more technical / condensed      |
| Alert State          | Soft high-contrast pulse           | Strong amber / red authoritative pulse   |

---

## 3. State Machine & Motion Language

Every state must be visually distinct within 200–300 ms.

### Shared States (both modes)
- **Idle / Dormant** — minimal ambient presence
- **Listening** — attentive “lean-in”
- **Thinking** — searching / computing motion (the latency sponge)
- **Speaking** — true voice-reactive
- **Delegating** — system-working indicator
- **Confirmation Required** — unmistakable alert
- **Media Reactive** — beat-driven

### Jarvis Mode Additional Richness
- Data streams flowing into the core during Thinking
- Expanding concentric rings on Listening
- Particle density and speed increase with cognitive load
- Energy lines appear when Canvas panels are active

Motion must always be driven by:
- Real microphone amplitude / pitch during Listening & Speaking
- Real audio analysis during Media mode
- Pipeline state during Thinking / Delegating

Never use pre-rendered loops that ignore actual audio.

---

## 4. Mode Transformation Sequence (Jarvis Activation)

When the wake word “Jarvis” is detected:

1. Current Aria Mode presence begins a short dissolve / energy gather (150–250 ms)
2. Arc-Reactor core materializes with rotating rings and particle birth
3. Optional short system boot line (“Systems online” or silent depending on preference)
4. Personality and visual density switch
5. Ready state is reached

Total transformation target: under 600–800 ms.  
It should feel powerful but never sluggish.

Reverse transformation (back to Aria Mode) can be softer and slightly longer.

---

## 5. Canvas Mode Layout Rules

- Panels are borderless and floating.
- They appear with a synchronized or staggered entrance linked to the core.
- Layout algorithm chooses arrangement based on number of panels and screen real estate:
  - 1 panel → centered or near core
  - 2–3 panels → fan or side-by-side
  - 4+ panels → grid or edge-docked with core as gravity center
- Visual linking (energy line or particle trail) is mandatory so the user understands ownership.
- Default lifetime: 30–90 seconds or until dismissed.
- Pinning makes a panel persistent across sessions until unpinned.
- Voice commands for layout: “move X to the left”, “make the chart bigger”, “dismiss all”, “pin the weather”.

---

## 6. Trust & Safety Visual Design

These elements are non-negotiable:

1. **Microphone State Indicator**  
   Persistent, small, always visible when the assistant is capable of listening.  
   Different appearance for “actively listening” vs “available but not listening”.

2. **Delegating State**  
   Must be clearly different from normal Thinking so the user knows a real system action is in progress.

3. **Confirmation State**  
   Highest visual priority. Color, motion, and optional subtle haptic/audio cue.  
   Cannot be missed.

4. **Privacy Controls**  
   One-tap mute / disable listening from the ambient indicator or Settings companion.

---

## 7. Interaction Model

### Activation
- Voice wake (dual)
- Keyboard shortcut
- Ambient indicator tap
- Future: gesture

### During Conversation
- Natural barge-in at any time
- Visual feedback that the interruption was received
- Context and references resolve across turns

### Confirmation Flow
1. Risk summary spoken + shown
2. Visual state → Confirmation
3. User says clear affirmative or cancels
4. Timeout → cancel
5. Result narrated + visual return to normal

### Canvas Interaction
- Voice primary
- Optional mouse / touch drag for power users
- Clear “dismiss” and “pin” affordances

---

## 8. Personality Expression Through Design

**Aria Mode**
- Softer language
- More concise answers by default
- Gentle motion
- Lower information density

**Jarvis Mode**
- More formal / precise language
- Higher information density
- Willingness to surface system status, alternatives, and deeper detail
- Slight dry wit allowed
- Visuals feel more “command center”

The personality matrix lives in the LLM system prompt + response style guidelines and is reinforced by the visual density difference.

---

## 9. Accessibility & Inclusivity

- All critical states must have non-color indicators (motion + optional sound)
- High contrast mode support
- Screen reader compatibility for the Settings companion and any text panels
- Configurable animation intensity (reduce motion)
- Voice confirmation must work for users who cannot use precise phrases (fallback to simple “yes” / “no”)

---

## 10. Settings Companion App (Lightweight)

A small, conventional application that controls:

- Wake word sensitivity and custom phrases
- Default mode preference
- Voice selection and cloning
- Visual theme intensity and reduce-motion
- Privacy: microphone history, data wipe, listening enable/disable
- Multi-user profiles
- Keyboard shortcuts
- Canvas default lifetime and pin behavior

This is the only traditional “app” the user ever opens. Everything else is the living overlay.

---

## 11. Motion & Timing Guidelines

- State transitions: 150–400 ms
- Mode transformation: 600–800 ms total
- Panel entrance: 300–600 ms with slight stagger
- Confirmation appearance: immediate and high priority
- Auto-dismiss of ephemeral panels: configurable, default 45–60 s of inactivity

All motion should feel physical and intentional, never bouncy or playful in a way that undermines trust.

---

## 12. Success Metrics for UI/UX

- Users can tell Listening vs Thinking vs Speaking at a glance
- Mode switch feels delightful rather than confusing
- Confirmation state is never missed
- Canvas panels feel “owned” by Aria rather than random windows
- Latency is masked so well that users describe the experience as “instant”
- Trust indicators are noticed and understood

---

This UI/UX specification exists to keep the visual and interaction design coherent as the system grows.  
Every new feature must respect the dual-mode identity, the truthful state language, and the trust requirements.

The goal is simple:  
When someone says “Jarvis”, the room should feel different.
