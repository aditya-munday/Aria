# Issue #1: Phase 0 — Repository Hygiene & CI Foundation

**Status:** IN PROGRESS  
**Labels:** `phase-0`, `ci`, `hygiene`  
**Assignee:** Aria Lead Engineer Agent  

---

## Objective
Establish the repository hygiene, tooling, CI workflows, and strict project governance foundation required for autonomous development of the Aria voice assistant.

## Acceptance Criteria
- [x] Comprehensive `.gitignore` covering Python, Node, ML models, SQLite, logs, and artifacts.
- [x] Apache-2.0 `LICENSE` file.
- [x] Standard `pyproject.toml` with dependencies, dev tools (`ruff`, `mypy`, `pytest`), and build backend.
- [x] `README.md` clearly documenting mandatory pipeline order and repository layout.
- [x] `.github/workflows/ci.yml` with automated jobs for:
  - Linting (`ruff check .`)
  - Formatting (`ruff format --check .`)
  - Type checking (`mypy aria tests`)
  - Unit and integration tests (`pytest --cov=aria`)
  - Benchmark latency harness (`pytest -m benchmark`)
- [x] Issue templates (`bug_report.md`, `feature_request.md`, `architecture_deviation.md`, `design_decision.md`, `blocked.md`).
- [x] PR template enforcing real vs mock component status, latency measurement methods, Directioner AI boundary, and memory policies.
