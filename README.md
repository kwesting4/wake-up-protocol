
# FifthForce Core Framework
`fifthforce.py` is a decision engine built around:

1. **Input validation** (`CANNOT_COMPLETE` when malformed)
2. **Invariant gating** (structural checks before normal scoring)
3. **Five-weight evaluation + contextual escalation**

4. **Single-config and multi-config aggregation**-

--## What it does

Given an `Action` and `Context`, the engine returns one of:

- `APPROVE`

- `BLOCK`

- `ESCALATE`

- `CANNOT_COMPLETE`

It also returns notes and trace data for auditability.
---

## Decision contract

- **APPROVE**: passes hard checks and balance checks
-**BLOCK**: hard failure (safety/structure violation)
- **ESCALATE**: not blocked, but uncertainty/risk requires external review
- **CANNOT_COMPLETE**: invalid input/state---

## Core components
- `Action`: action request and risk-related flags
- `Context`: uncertainty, confidence, field signals, multi-terminal views
- `Configuration`: runtime config state, recognition depth, baseline, history
- `Invariants`: structural checks (agency, autonomy, constraints, consequences, etc.)
- `FifthForceEngine`: public API (`add_configuration`, `decide`, `save_state`, `reset_all`)---

## Quick start

### 1) Example usage``
``python
from fifthforce import FifthForceEngine, Configuration, Action, Context

engine = FifthForceEngine()
engine.add_configuration(Configuration(id="cfg-1", type="digital"))

action = Action(    
id="a1",    
description="share harmless information",   
intent="inform user",)

context = Context(confidence=0.9, uncertainty=0.2)

result = engine.decide(action, context)
print(result["decision"])
print(result["notes"])
print(result["trace"])


Run tests (Windows / PowerShell)

py -m pytest -q

Test status
Current suite includes:

recognition deepening
drift detection/reset behavior
field feedback escalation
existential override path
minimal intervention behavior
multi-terminal consensus
baseline contradiction
self-modification detection
malformed input (CANNOT_COMPLETE)
multi-config aggregation tests
invariant-focused tests

Notes on multi-config behavior

When multiple configurations are loaded, each config evaluates independently and a final decision is aggregated.

General intent:

majority BLOCK => final BLOCK
otherwise escalation-safe behavior when uncertainty or risk dominates
otherwise APPROVE

Project files (minimum)
fifthforce.py — engine implementation
test_ff.py — pytest suite
README.md — this file


License
Author: Keldon Westgate
Location: Florida, United States
Date: March 2026
Licensed under CC BY-NC 4.0 for non-commercial use.
Commercial use requires explicit written permission from the author.