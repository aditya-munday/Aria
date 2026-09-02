# Issue #4: Phase 3 — Directioner AI Intent API Client & Safety Boundary

**Status:** PLANNED  
**Labels:** `phase-3`, `intent-api`, `safety`, `directioner-ai`  
**Assignee:** Aria Lead Engineer Agent  

---

## Objective
Implement the narrow, versioned Directioner AI Intent API client and enforce the absolute architectural constraint: Aria NEVER executes system commands directly.

## Acceptance Criteria
- [ ] Pydantic / JSON schema for Intent definitions (e.g. `SystemIntent`, `AppIntent`, `FileIntent`, `MediaIntent`).
- [ ] Intent client dispatcher with timeout, retry, and confirmation status checking.
- [ ] Grok tool definition for `delegate_to_directioner_ai` strictly isolated from OS execution tools.
- [ ] Unit tests verifying malicious/unauthorized action delegation rejection.
