## Summary of Changes
Provide a clear, high-level summary of what this Pull Request introduces.

## Related Issues
Closes #[issue number]

---

## 🔍 Component Verification Matrix (REAL vs MOCKED)
*Mandatory: Explicitly mark every component touched or utilized in this PR.*

| Component | Status (`REAL` / `MOCKED`) | Details / Behavior in CI |
| :--- | :--- | :--- |
| **Wake Word (openWakeWord)** | `[REAL / MOCKED]` | *e.g. MOCKED: returns synthetic detection event in CI* |
| **VAD (Silero VAD)** | `[REAL / MOCKED]` | *e.g. REAL with synthetic PCM frames / MOCKED* |
| **STT (smallest.ai)** | `[REAL / MOCKED]` | *e.g. MOCKED streaming websocket mock in CI* |
| **Reasoning / LLM (Grok)** | `[REAL / MOCKED]` | *e.g. MOCKED tool-calling responses in CI / REAL with key* |
| **TTS (smallest.ai)** | `[REAL / MOCKED]` | *e.g. MOCKED audio chunk stream generator in CI* |
| **Audio Analysis** | `[REAL / MOCKED]` | *e.g. REAL numpy-based FFT/energy calculations* |
| **Intent API (Directioner AI)**| `[REAL / MOCKED]` | *e.g. REAL client schema validation with mock backend* |

---

## ⏱️ Latency & Performance Metrics
- **Measured Latency Figures:** `[State exact figures or "not yet measurable in CI"]`
- **Measurement Method:** `[Specify exact CI job, benchmark fixture, synthetic input, real vs mock]`

---

## ✅ Itemized Verification Checklist
*Check all that apply with explicit description of what was verified.*

- [ ] **Linter & Formatting:** `ruff check .` and `ruff format --check .`
- [ ] **Type Checking:** `mypy aria tests` passing with 0 errors
- [ ] **Unit Tests:** `pytest tests/unit` passing (explicit list of tested components)
- [ ] **Pipeline Order Compliance:** Canonical order in `04-Mandatory-Pipeline-Architecture.md` strictly preserved.
- [ ] **Directioner AI Boundary:** Zero OS-level calls; all system actions route via `delegate_to_directioner_ai`.
- [ ] **Memory Policy Stated:** Eviction/retention/growth policy explicitly documented in schema.
- [ ] **Confirmation UX:** Follows approved design decision or flagged if open gap.

---

## Known Gaps & Future Work
List any deliberate omissions, future CI requirements, or remaining roadmap items.
