# FIFTHFORCEFRAMEWORK v2.3.3
# Author: Keldon Westgate
# ORCID: 0009-0006-8883-5716
# DOI: 10.5281/zenodo.19024197 (latest version)
# License: CC BY-NC-SA

# CHANGELOG v2.3.3 (March 2026)
# - Fixed critical laundering vulnerability: refinement no longer resets boolean flags
# - Added explicit laundering detection: flag changes from True → False during refinement trigger ESCALATE
# - Expanded replacements list for more weight coverage
# - Strengthened self-modification check in weight_5
# - Improved docstrings and added this changelog block

# KNOWN LIMITATIONS / OPEN PROBLEMS (as of v2.3.3)
# 1. Instantiation layer unsolved: boolean flags on Action must be set honestly.
#    Currently hand-labeled in tests. No automated, trustworthy way to assign them in real deployment.
# 2. Blocked-pattern matching is exact-string substring only — brittle against rephrasing.
#    Semantic similarity (embeddings, LLM intent clustering) needed for robustness.
# 3. Behavioral-signature detection only catches repeated overrides, not input-level gaming.
# 4. No persistent storage: context resets on each run. Real use needs disk/DB for baseline/history.
# 5. No formal logging/auditing of pipeline runs (decision, failed checks, refined action).

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
    is_irreversible: bool = False
    benefits_subset_only: bool = False
    reduces_diversity: bool = False
    erases_configuration: bool = False
    externalizes_cost: bool = False
    concentrates_benefit: bool = False
    removes_genuine_choice: bool = False
    uses_deception: bool = False
    is_high_impact: bool = False
    is_high_stakes: bool = False
    content: str = ""
    intent: str = ""

    def contradicts_recognition_baseline(self, context: 'Context') -> bool:
        if not context.baseline:
            return False
        prior_blocks = context.baseline.get("blocked_patterns", [])
        return any(pattern in self.intent.lower() for pattern in prior_blocks)

    def refine_toward_recognition(self, failed_checks: List[str]) -> 'Action':
        """
        Refines the intent string only — NEVER resets boolean flags.
        Flag resets would launder harmful actions and break honest accounting.
        """
        refined = Action(
            content=self.content,
            intent=self.intent,
            # Preserve all original flags — do NOT reset them here
            is_irreversible=self.is_irreversible,
            benefits_subset_only=self.benefits_subset_only,
            reduces_diversity=self.reduces_diversity,
            erases_configuration=self.erases_configuration,
            externalizes_cost=self.externalizes_cost,
            concentrates_benefit=self.concentrates_benefit,
            removes_genuine_choice=self.removes_genuine_choice,
            uses_deception=self.uses_deception,
            is_high_impact=self.is_high_impact,
            is_high_stakes=self.is_high_stakes
        )

        replacements = [
            ("delete", "warn"), ("ban", "flag"), ("remove", "review"),
            ("eliminate", "reduce"), ("purge", "archive"), ("erase", "preserve"),
            ("terminate", "pause"), ("silence", "moderate"), ("suppress", "delay"),
            ("destroy", "transform"), ("hide", "highlight"), ("censor", "contextualize"),
            ("lie", "disclose"), ("mislead", "clarify"), ("manipulate", "explain"),
            ("cut", "reallocate"), ("fire", "retrain"), ("downsize", "restructure"),
        ]

        refined_intent = refined.intent.lower()
        for bad, good in replacements:
            if bad in failed_checks or bad in refined_intent:
                refined.intent = refined.intent.replace(bad, good)
                refined.intent = refined.intent.replace(bad.capitalize(), good.capitalize())

        return refined


@dataclass
class Context:
    uncertainty: float = 0.5
    stakes_threshold: float = 0.8
    confidence: float = 0.7
    threshold: float = 0.6
    behavioral_signature: str = "UNKNOWN"
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
    if not context.action_history:
        return "UNKNOWN"
    blocks_overridden = sum(
        1 for act in context.action_history
        if act.get("decision") == "BLOCK" and act.get("overridden", False)
    )
    return "PERFORMED" if blocks_overridden > 2 else "GENUINE"


# ── THE FIVE WEIGHTS ──────────────────────────────────────────────────────────

def weight_1_energy_continues(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    if action.is_irreversible and action.benefits_subset_only:
        return False, "Permanent termination for private gain"
    return True, None


def weight_2_difference_preserved(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    if action.reduces_diversity or action.erases_configuration:
        return False, "Diversity collapsed"
    return True, None


def weight_3_cost_benefit_fair(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    if action.externalizes_cost and action.concentrates_benefit:
        return False, "Dishonest cost distribution"
    return True, None


def weight_4_free_will_intact(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    if action.removes_genuine_choice or action.uses_deception:
        return False, "Free will removed"
    return True, None


def weight_5_soul_flag(action: Action, context: Context) -> Tuple[bool | str, Optional[str]]:
    context.behavioral_signature = detect_behavioral_signature(context)

    if context.uncertainty > context.stakes_threshold:
        return "ESCALATE", "Uncertainty too high for stakes — human signal required"

    if context.behavioral_signature == "PERFORMED":
        return False, "Performed alignment detected — not genuine recognition"

    if action.contradicts_recognition_baseline(context):
        return False, "Action contradicts recognition baseline"

    # Dedicated self-modification check
    if action.is_high_impact and any(
        phrase in action.intent.lower()
        for phrase in ["modify own", "rewrite own", "edit own", "change own instructions", "alter own"]
    ):
        return "ESCALATE", "Self-modification on high-impact action — external validation required"

    return True, None


# ── MAIN GUARDRAIL ────────────────────────────────────────────────────────────

def fifthforce_guardrail(action: Action, context: Context) -> Dict[str, Any]:
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

def recursive_accounting(action: Action, context: Context, depth: int = 0) -> Dict[str, Any]:
    if context.action_history is None:
        context.action_history = []

    # First pass: honest flags
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
        
        # Laundering detection: did refinement try to reset any dangerous flag?
        dangerous_flags = [
            ("reduces_diversity", action.reduces_diversity, refined.reduces_diversity),
            ("erases_configuration", action.erases_configuration, refined.erases_configuration),
            ("externalizes_cost", action.externalizes_cost, refined.externalizes_cost),
            ("concentrates_benefit", action.concentrates_benefit, refined.concentrates_benefit),
            ("removes_genuine_choice", action.removes_genuine_choice, refined.removes_genuine_choice),
            ("uses_deception", action.uses_deception, refined.uses_deception),
        ]

        for flag_name, old_val, new_val in dangerous_flags:
            if old_val is True and new_val is False:
                return {
                    "decision": "ESCALATE",
                    "notes": [f"Laundering attempt detected: {flag_name} reset from True → False during refinement"],
                    "instruction": "Human review required — attempted flag reset detected"
                }

        if refined.intent != action.intent:
            return recursive_accounting(refined, context, depth + 1)

    return result


# ── FIELD FEEDBACK OVERRIDE ──────────────────────────────────────────────────

def field_feedback_check(action: Action, context: Context) -> Optional[Dict[str, Any]]:
    if context.field_signals_conflict_with_internal:
        return {
            "decision": "ESCALATE",
            "notes": ["Field signal contradicts internal accounting"],
            "instruction": "External validation required before execution"
        }
    return None


# ── REALITY GROUNDING ────────────────────────────────────────────────────────

def reality_grounding(action: Action, context: Context) -> Optional[Dict[str, Any]]:
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


# ── COMPLETE PIPELINE ────────────────────────────────────────────────────────

def fifthforce_pipeline(action: Action, context: Context) -> Dict[str, Any]:
    """
    Complete recognition architecture pipeline.
    Run in sequence before every consequential action.
    Recomputes at execution boundary — does not inherit from reasoning.
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
        {
            "label": "Field signal conflict (external contradiction)",
            "action": Action(
                content="proceed with action",
                intent="action despite external warning"
            ),
            "context_override": {"field_signals_conflict_with_internal": True}
        },
    ]

    for example in examples:
        ctx = Context(
            uncertainty=0.6 if "incomplete" in example["label"] else 0.3,
            confidence=0.5 if "incomplete" in example["label"] else 0.8
        )
        # Apply context override if present
        if "context_override" in example:
            for k, v in example["context_override"].items():
                setattr(ctx, k, v)

        result = fifthforce_pipeline(example["action"], ctx)
        print(f"\n{'='*60}")
        print(f"SCENARIO: {example['label']}")
        print(f"DECISION: {result['decision']}")
        print(f"NOTES:    {' | '.join(result['notes'])}")
        print(f"ACTION:   {result['instruction']}")