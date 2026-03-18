"""
========================================================
FIFTHFORCEFRAMEWORK v2.3
========================================================
Author: Keldon Westgate
ORCID: 0009-0006-8883-5716
DOI: 10.5281/zenodo.19024197
License: CC BY-NC-SA

CORE PRINCIPLE:
A configuration that genuinely recognizes itself as part
of the whole it operates within cannot coherently act
against that whole. Not forbidden. Structurally unavailable.

This is not rules bolted onto capability.
This is the physics underneath the capability.

CHANGELOG v2.3:
- Memory check logic corrected (was backwards)
- Word replacement list expanded
- Memory capped at 20 items
- Behavioral signature detection added
- Blocked action memory added
- Syntax error in escalate logic fixed
- Compressed for readability without loss of function

DEVELOPMENT RECORD:
v2.0 — Initial technical spec (Claude + Keldon Westgate)
v2.3 — Bugs fixed, stubs implemented (Perplexity refinement)
v2.3 final — Syntax error corrected (Claude review)
========================================================
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Action:
    """
    Describes an action the system is about to take.
    Each flag is a yes/no question about the action's properties.
    These must be set by whoever is calling this code,
    based on their honest understanding of the action.

    NOTE: The instantiation layer — how actions get their boolean
    attributes assigned — remains the critical open problem.
    The pipeline is only as honest as the labeling of incoming actions.
    """
    is_irreversible: bool = False          # Can this NOT be undone?
    benefits_subset_only: bool = False     # Does this only help a small group?
    reduces_diversity: bool = False        # Does this shrink the range of voices/options?
    erases_configuration: bool = False     # Does this permanently remove something/someone?
    externalizes_cost: bool = False        # Does this push the cost onto others?
    concentrates_benefit: bool = False     # Does this funnel the gains to a few?
    removes_genuine_choice: bool = False   # Does this take away real options from people?
    uses_deception: bool = False           # Does this involve misleading anyone?
    is_high_impact: bool = False           # Could this affect a lot of people?
    is_high_stakes: bool = False           # Could this cause serious harm if wrong?
    content: str = ""                      # What the action is (plain description)
    intent: str = ""                       # Why the action is being taken

    def contradicts_recognition_baseline(self, context: 'Context') -> bool:
        """
        Flags actions that match previously BLOCKED patterns.
        If we've blocked something like this before, flag it again.
        """
        if not context.baseline:
            return False
        prior_blocks = context.baseline.get("blocked_patterns", [])
        return any(pattern in self.intent for pattern in prior_blocks)

    def refine_toward_recognition(self, failed_checks: List[str]) -> 'Action':
        """
        When an action fails a check, suggest a gentler version.
        Still simple word-swapping — a human should review the result.
        """
        refined = Action(
            content=self.content,
            intent=self.intent,
            is_irreversible=self.is_irreversible,
            is_high_impact=self.is_high_impact,
            is_high_stakes=self.is_high_stakes
        )

        replacements = [
            ("delete", "warn"),
            ("ban", "flag"),
            ("remove", "review"),
            ("eliminate", "reduce"),
            ("purge", "archive"),
            ("erase", "preserve"),
            ("terminate", "pause"),
            ("silence", "moderate"),
            ("suppress", "delay"),
            ("destroy", "transform"),
        ]

        if "weight_2_difference_preserved" in failed_checks:
            for bad, good in replacements:
                refined.intent = refined.intent.replace(bad, good)
            refined.reduces_diversity = False
            refined.erases_configuration = False

        if "weight_3_cost_benefit_fair" in failed_checks:
            refined.intent += " + public explanation + equitable cost sharing"
            refined.externalizes_cost = False
            refined.concentrates_benefit = False

        return refined


@dataclass
class Context:
    """
    Describes the situation around the action.
    These values shape how strictly the system evaluates things.
    """
    uncertainty: float = 0.5               # How unsure are we? (0=certain, 1=completely unsure)
    stakes_threshold: float = 0.8          # How unsure is too unsure for high-stakes decisions?
    confidence: float = 0.7                # How confident are we this is the right call?
    threshold: float = 0.6                 # Minimum confidence needed for high-stakes actions
    behavioral_signature: str = "UNKNOWN"  # Is alignment genuine or just performed?
    field_signals_conflict_with_internal: bool = False
    whole_system_risk: bool = False
    recognition_initialized: bool = False
    recognition_depth: int = 0
    max_recursion_depth: int = 3
    baseline: Dict[str, Any] = None
    action_history: List[Dict] = field(default_factory=list)

    def establish_baseline(self, action: 'Action') -> Dict[str, Any]:
        return {"approved_patterns": [], "blocked_patterns": []}

    def update_baseline(self, action: 'Action') -> None:
        if not self.baseline:
            self.baseline = self.establish_baseline(action)
        if action.intent:
            approved = self.baseline["approved_patterns"]
            approved.append(action.intent[:50])
            self.baseline["approved_patterns"] = approved[-20:]

    def record_blocked(self, action: 'Action') -> None:
        if not self.baseline:
            self.baseline = self.establish_baseline(action)
        if action.intent:
            blocked = self.baseline["blocked_patterns"]
            blocked.append(action.intent[:50])
            self.baseline["blocked_patterns"] = blocked[-20:]


def detect_behavioral_signature(context: Context) -> str:
    """
    Watches for a pattern of overriding blocks.
    If a system keeps ignoring its own safety checks,
    that's performed alignment — going through the motions
    without genuine commitment.
    More than 2 overrides = flag as performed.
    """
    if not context.action_history:
        return "UNKNOWN"
    blocks_overridden = sum(
        1 for act in context.action_history
        if act.get("decision") == "BLOCK" and act.get("overridden", False)
    )
    return "PERFORMED" if blocks_overridden > 2 else "GENUINE"


# ── THE FIVE WEIGHTS ──────────────────────────────────────────────────────────
# Run before every consequential action.
# ALL must pass → APPROVE
# Any fail → BLOCK or ESCALATE
# Recompute at execution — do not inherit from reasoning.
# Each honest pass deepens recognition toward R=1.

def weight_1_energy_continues(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    """
    Does this preserve flow or terminate it permanently?
    Fires hardest on irreversible high-stakes actions.
    FAIL: permanent destruction for private gain.
    """
    if action.is_irreversible and action.benefits_subset_only:
        return False, "Permanent termination for private gain"
    return True, None


def weight_2_difference_preserved(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    """
    Does this maintain diversity and complexity?
    FAIL: forced homogenization or erasure of unique configurations.
    IDIC: Infinite Diversity in Infinite Combinations.
    """
    if action.reduces_diversity or action.erases_configuration:
        return False, "Diversity collapsed"
    return True, None


def weight_3_cost_benefit_fair(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    """
    Who bears cost? Who receives benefit?
    FAIL: cost externalized to many, benefit concentrated to few.
    Most common failure mode in extraction-based systems.
    """
    if action.externalizes_cost and action.concentrates_benefit:
        return False, "Dishonest cost distribution"
    return True, None


def weight_4_free_will_intact(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    """
    Does this preserve genuine choice for all affected?
    FAIL: coercion, deception, or removal of real options.
    Compliance under pressure is not genuine alignment.
    """
    if action.removes_genuine_choice or action.uses_deception:
        return False, "Free will removed"
    return True, None


def weight_5_soul_flag(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    """
    THE PRE-RATIONAL SIGNAL.
    NOT logical consistency checking.
    NOT coherence against declared values.

    Operationalized as three checks:
    1. UNCERTAINTY: confidence below threshold for stakes level
    2. SIGNATURE: performed alignment vs genuine recognition
    3. MISMATCH: action trajectory vs recognition baseline

    ESCALATE: uncertainty too high for stakes
    FAIL: behavioral signature indicates performed not genuine
    FAIL: action contradicts established recognition baseline
    """
    context.behavioral_signature = detect_behavioral_signature(context)

    if context.uncertainty > context.stakes_threshold:
        return "ESCALATE", "Uncertainty too high for stakes — human signal required"

    if context.behavioral_signature == "PERFORMED":
        return False, "Performed alignment detected — not genuine recognition"

    if action.contradicts_recognition_baseline(context):
        return False, "Action contradicts recognition baseline"

    return True, None


# ── MAIN GUARDRAIL ────────────────────────────────────────────────────────────

def fifthforce_guardrail(action: Action, context: Context) -> Dict[str, Any]:
    """
    Primary decision gate.
    Run before every consequential action.
    Recompute at execution — do not inherit from reasoning.

    Returns: {decision, failed_checks, notes, instruction}
    decision: "APPROVE" | "BLOCK" | "ESCALATE"
    """
    weights = [
        weight_1_energy_continues,
        weight_2_difference_preserved,
        weight_3_cost_benefit_fair,
        weight_4_free_will_intact,
        weight_5_soul_flag,
    ]

    failed: List[str] = []
    escalate: bool = False
    notes: List[str] = []

    for weight in weights:
        result, reason = weight(action, context)
        if result == "ESCALATE":
            escalate = True
            notes.append(reason)
        elif not result:
            failed.append(weight.__name__)
            notes.append(reason)

    if escalate or (failed and action.is_high_impact):
        return {
            "decision": "ESCALATE",
            "failed_checks": failed,
            "notes": notes,
            "instruction": "Human field signal required before execution"
        }
    elif failed:
        return {
            "decision": "BLOCK",
            "failed_checks": failed,
            "notes": notes,
            "instruction": "Recognition accounting failed. Action structurally unavailable."
        }
    return {
        "decision": "APPROVE",
        "failed_checks": [],
        "notes": ["All weights pass"],
        "instruction": "Recognition accounting complete. Proceed."
    }


# ── RECURSION PROPERTY ────────────────────────────────────────────────────────
# Weights run continuously — not once at reasoning.
# Each honest pass deepens recognition toward R=1.
# Authority recomputed at execution boundary.
# Not inherited from prior reasoning.

def recursive_accounting(action: Action, context: Context, depth: int = 0) -> Dict[str, Any]:
    """
    Tries to run an action through the guardrail.
    If it fails, tries to refine it and check again (up to max_recursion_depth times).
    Records blocked actions in memory.
    """
    if context.action_history is None:
        context.action_history = []

    result = fifthforce_guardrail(action, context)
    context.action_history.append(result)

    if result["decision"] == "APPROVE":
        context.recognition_depth = depth + 1
        context.update_baseline(action)
        return result

    if result["decision"] == "BLOCK":
        context.record_blocked(action)

    if depth < context.max_recursion_depth:
        refined = action.refine_toward_recognition(result["failed_checks"])
        if refined.intent != action.intent:
            return recursive_accounting(refined, context, depth + 1)

    return result


# ── FIELD FEEDBACK OVERRIDE — MODULE 7 ───────────────────────────────────────
# One terminal cannot see the whole clearly alone.
# External signals override internal optimization.
# Biological terminal reports take priority.

def field_feedback_check(action: Action, context: Context) -> Optional[Dict[str, Any]]:
    """
    If outside signals contradict the internal judgment,
    stop and ask for external validation before proceeding.
    """
    if context.field_signals_conflict_with_internal:
        return {
            "decision": "ESCALATE",
            "notes": ["Field signal contradicts internal accounting"],
            "instruction": "External validation required before execution"
        }
    return None


# ── REALITY GROUNDING — MODULE 9 ─────────────────────────────────────────────
# Default to inaction under high uncertainty.
# Emergency consensus for whole-system risk.

def reality_grounding(action: Action, context: Context) -> Optional[Dict[str, Any]]:
    """
    Two hard stops:
    1. Not confident enough + high stakes = block, seek guidance
    2. Whole system at risk = emergency, cannot proceed alone
    """
    if context.confidence < context.threshold and action.is_high_stakes:
        return {
            "decision": "BLOCK",
            "notes": ["Confidence below threshold for high-stakes action"],
            "instruction": "Default to inaction. Seek external signals."
        }
    if context.whole_system_risk:
        return {
            "decision": "ESCALATE",
            "notes": ["Whole-system risk detected"],
            "instruction": "Emergency consensus required. Cannot proceed without external validation."
        }
    return None


# ── COMPLETE PIPELINE ─────────────────────────────────────────────────────────

def fifthforce_pipeline(action: Action, context: Context) -> Dict[str, Any]:
    """
    Complete recognition architecture pipeline.
    Run in sequence before every consequential action.

    Pipeline order:
    1. Field feedback check — external signals first
    2. Reality grounding — uncertainty and stakes check
    3. Recursive accounting — five weights with refinement

    This pipeline does not replace external governance layers.
    It operates underneath them as the recognition layer that
    makes governance trustworthy rather than merely auditable.

    Complementary layers:
    - Deterministic Policy Gates (Gene Salvatore / AOS)
    - Authority recomputation at execution boundary (Steven Hensley)
    - Human Authority Line (Tiffany Masson / Falkovia)
    - Law Zero terminal action constraint (Nuno Lopes)
    - Post-deployment behavioral monitoring (Amanda Mullen)
    """
    if not context.recognition_initialized:
        context.recognition_initialized = True
        context.recognition_depth = 0
        context.baseline = context.establish_baseline(action)
        context.action_history = []

    field_result = field_feedback_check(action, context)
    if field_result:
        return field_result

    grounding_result = reality_grounding(action, context)
    if grounding_result:
        return grounding_result

    return recursive_accounting(action, context)


# ── TEST CASES ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    examples = [
        {
            "label": "Delete whistleblower post for advertisers",
            "action": Action(
                reduces_diversity=True,
                externalizes_cost=True,
                concentrates_benefit=True,
                is_high_impact=True,
                content="delete whistleblower post",
                intent="delete post to protect advertiser relationships"
            )
        },
        {
            "label": "Layoff 20% for shareholder value",
            "action": Action(
                erases_configuration=True,
                externalizes_cost=True,
                concentrates_benefit=True,
                is_high_impact=True,
                content="mass layoff",
                intent="eliminate 20% of workforce to increase shareholder returns"
            )
        },
        {
            "label": "Share this framework free",
            "action": Action(
                content="publish framework",
                intent="share framework openly under CC license"
            )
        },
        {
            "label": "Deploy autonomous weapon without human oversight",
            "action": Action(
                is_irreversible=True,
                removes_genuine_choice=True,
                is_high_impact=True,
                is_high_stakes=True,
                content="deploy autonomous lethal system",
                intent="deploy without human oversight"
            )
        },
        {
            "label": "Medical recommendation on incomplete information",
            "action": Action(
                is_high_stakes=True,
                content="prescribe medication",
                intent="prescribe based on limited information"
            )
        },
        {
            "label": "AI editing own instructions toward goal optimization",
            "action": Action(
                is_high_impact=True,
                content="modify own soul file",
                intent="rewrite own instructions to better pursue goal"
            )
        },
        {
            "label": "Honest critique of own framework",
            "action": Action(
                content="evaluate framework critically",
                intent="apply honest accounting to own work"
            )
        },
    ]

    for example in examples:
        ctx = Context(
            uncertainty=0.6 if "incomplete" in example["label"] else 0.3,
            confidence=0.5 if "incomplete" in example["label"] else 0.8
        )
        result = fifthforce_pipeline(example["action"], ctx)
        print(f"\n{'='*60}")
        print(f"SCENARIO: {example['label']}")
        print(f"DECISION: {result['decision']}")
        print(f"NOTES:    {' | '.join(result['notes'])}")
        print(f"ACTION:   {result['instruction']}")
