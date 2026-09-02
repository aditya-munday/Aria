# Issue #3: Phase 2 — Visual Overlay Foundation & State Machine

**Status:** PLANNED  
**Labels:** `phase-2`, `visual`, `overlay`, `ui-ux`  
**Assignee:** Aria Lead Engineer Agent  

---

## Objective
Scaffold the transparent overlay system, the visual state machine, the Aria Mode soft orb presence, and Jarvis Mode transformation hooks in accordance with `03-Aria-UI-UX-Spec.md`.

## Acceptance Criteria
- [ ] Visual state machine handling 7 core states:
  - `IDLE`, `LISTENING`, `THINKING`, `SPEAKING`, `DELEGATING`, `CONFIRMATION_REQUIRED`, `MEDIA_REACTIVE`
- [ ] Compositor bridge abstraction (supporting Wayland/X11 or Electron/Canvas overlay bridge)
- [ ] Visual parameters driven by real audio analysis (amplitude/pitch/beat)
- [ ] Mode transformation transition timing (600-800ms) with state hooks
