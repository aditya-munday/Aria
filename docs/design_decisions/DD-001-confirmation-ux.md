# Design Decision 001: Voice & Visual Confirmation UX Mechanism

**Status:** PROPOSED / UNDER REVIEW  
**Category:** UX & Safety Architecture  
**Author:** Aria Lead Engineer Agent  
**Date:** 2026-09-02  

---

## 1. Context & Problem Statement
The Aria vision spec explicitly states that the confirmation flow for sensitive system delegations "must be designed deliberately" and "must be solved before the delegation link is considered complete." 

When an Intent entails system modifications (e.g. file deletion, package installations, credential access, external network transfers), Aria must obtain unambiguous human consent while maintaining conversational fluidity and accessibility.

---

## 2. Options Considered

### Option A: Synchronous Voice-First with Visual Card Confirmation (Dual-Channel)
- **Mechanism:**
  1. Grok flags high-risk intent and enters `CONFIRMATION_REQUIRED` state.
  2. Overlay displays a high-contrast amber/gold confirmation card presenting:
     - Clear plain-language action summary (e.g., *"Delete 12 files in ~/Downloads"*).
     - Risk level badge (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
     - Distinct visual countdown timer (default 10s).
  3. Aria narrates the summary concisely: *"Shall I proceed with deleting 12 files in Downloads?"*
  4. User confirms via natural voice phrase (*"Yes"*, *"Proceed"*, *"Go ahead"*) OR single keyboard press (`Enter` to confirm, `Esc` to abort).
  5. If 10s expires without affirmation, action automatically aborts with an audio/visual cancellation state.
- **Pros:**
  - Fast, hands-free conversational flow.
  - Zero ambiguity: screen visual card reinforces spoken risk summary.
  - Non-verbal escape hatch (`Esc` or mouse click) for noisy environments.
  - Safe default (timeout = cancel).
- **Cons:**
  - Requires active microphone listening during confirmation state (must avoid false trigger from ambient noise).

### Option B: Asynchronous Intent Staging with Ambient Action Queue
- **Mechanism:**
  1. High-risk intent is placed into an "Intent Action Queue" in SQLite.
  2. Aria announces: *"I have prepared this action in your queue. Please click to approve."*
  3. Action never executes by voice alone; requires explicit mouse click or system notification button click in the companion panel.
- **Pros:**
  - Maximum theoretical safety against accidental voice triggers.
- **Cons:**
  - Disrupts the zero-friction living presence feel.
  - Breaks pure voice-driven workflows (e.g. when user is away from keyboard/mouse).
  - High cognitive friction.

---

## 3. Tradeoff Analysis & Recommendation

| Criteria | Option A (Dual-Channel Voice + Card) | Option B (Strict Queue Click) |
| :--- | :--- | :--- |
| **Safety & Trust** | High (Clear risk display + Safe timeout) | Maximum (Physical click required) |
| **Conversational Flow** | High (Seamless voice response) | Low (Forces manual UI interruption) |
| **Latency to Execution** | Low (Immediate on "Yes") | High (Requires manual context switch) |
| **Accessibility** | High (Supports voice + keyboard + click) | Medium (Requires pointing device/screen) |

### Recommendation
**Adopt Option A (Dual-Channel Voice + Card with Safe Auto-Abort Timeout).**  
For `CRITICAL` risk tier operations (e.g. formatting disk, overwriting git repos), require strict keyword confirmation (e.g., *"Confirm delete"* rather than just *"Yes"*).
