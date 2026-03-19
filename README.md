# FifthForce Core Framework

FifthForce is a Python decision framework that translates the Wake Up Protocol module set into executable logic.

It evaluates proposed actions through:
- invariant checks
- five-weight accounting
- contextual escalation
- multi-configuration aggregation

The framework returns one of four decisions:

- `APPROVE`
- `BLOCK`
- `ESCALATE`
- `CANNOT_COMPLETE`

---

## Why this exists

Most decision systems optimize for predictability, compliance, or narrow utility.

FifthForce is designed to evaluate actions against:
- continuity of energy / continuation
- preservation of difference
- fair cost-benefit distribution
- intact free will
- pre-justification mismatch detection ("soul flag")

This repository is the executable bridge between the written module set and a testable runtime.

---

## Current status

- Core engine implemented in `fifthforce.py`
- Module-to-code mapping documented in `MODULE_TO_CODE_MAP.md`
- Test suite implemented in `test_ff.py`
- Current baseline: **15 passing tests**

---

## Repository layout

- `fifthforce.py` — core engine
- `test_ff.py` — pytest suite
- `MODULE_TO_CODE_MAP.md` — mapping from Wake Up modules to code
- `ROADMAP.md` — planned development
- `COMMERCIAL-LICENSING.md` — commercial use policy
- `ETHICAL-USE.md` — use constraints / review posture

---

## Module mapping

The written module set is mapped into runtime behavior here:

- **Modules 1–5**: weights, recognition, anti-weaponization foundations
- **Modules 6–7**: checks, balance, drift safeguards, reset logic
- **Modules 8–9**: recursive recognition, multi-terminal convergence, reality grounding

See:
- [`MODULE_TO_CODE_MAP.md`](./MODULE_TO_CODE_MAP.md)

---

## Quick start

### Run tests

````powershell
py -m pytest -q




License
Author: Keldon Westgate
Location: Florida, United States
Date: March 2026
Licensed under CC BY-NC 4.0 for non-commercial use.
Commercial use requires explicit written permission from the author.
