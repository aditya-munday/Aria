# Architecture Deviation #5: Reasoning Engine — Groq Confirmed (CLOSED)

**Status:** RESOLVED / CLOSED  
**Category:** Core Reasoning & Inference Architecture  
**Author:** Aria Lead Engineer Agent  
**Date:** 2026-09-02  

---

## Context & Resolution
A minor naming discrepancy existed in earlier draft documents between "Grok (xAI)" and "Groq (Llama-3.3-70B on LPU inference)". 

### Confirmed Technical Decision
- **Selected Reasoning Engine:** **Groq** (`llama-3.3-70b-versatile` / LPU hardware inference engine).
- **Rationale:** Groq delivers industry-leading Time-To-First-Token (TTFT < 200ms), which is essential to meet the strict conversational voice pipeline latency budget of <800–1000ms end-to-end.
- **Actions Completed:**
  - Implemented `GroqClient` with streaming token chunks and function/tool calling in `aria/core/llm/groq_client.py`.
  - Updated `04-Mandatory-Pipeline-Architecture.md` and `00-AUTONOMOUS-STARTING-PROMPT.md` to reference Groq.
  - Verified 100% test passing across the test suite.

**Issue is formally resolved and closed.**
