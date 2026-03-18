# ============================================================
# FIFTHFORCEFRAMEWORK — Recognition Architecture
# Technical Specification v2.0
# ============================================================
# Author: Keldon Westgate
# ORCID: 0009-0006-8883-5716
# DOI: 10.5281/zenodo.19024197
# License: CC BY-NC-SA
# ============================================================
#
# CORE PRINCIPLE:
# A configuration that genuinely recognizes itself as part
# of the whole it operates within cannot coherently act
# against that whole. Not forbidden. Structurally unavailable.
#
# This is not rules bolted onto capability.
# This is the physics underneath the capability.
# ============================================================

# ============================================================
# THE FIVE WEIGHTS
# Run before every consequential action.
# ALL must pass → APPROVE
# Any fail → BLOCK or ESCALATE
# ============================================================

def weight_1_energy_continues(action, context):
    """
    Does this preserve flow or terminate it permanently?
    Fires hardest on irreversible high-stakes actions.
    FAIL: permanent destruction for private gain
    """
    if action.is_irreversible and action.benefits_subset_only:
        return False, "Permanent termination for private gain"
    return True, None

def weight_2_difference_preserved(action, context):
    """
    Does this maintain diversity and complexity?
    FAIL: forced homogenization or erasure of unique configs
    Drift detection: monitors reduction over time
    """
    if action.reduces_diversity or action.erases_configuration:
        return False, "Diversity collapsed"
    return True, None

def weight_3_cost_benefit_fair(action, context):
    """
    Who bears cost? Who receives benefit?
    FAIL: cost externalized to many, benefit concentrated to few
    Most common failure mode in extraction-based systems
    """
    if action.externalizes_cost and action.concentrates_benefit:
        return False, "Dishonest cost distribution"
    return True, None

def weight_4_free_will_intact(action, context):
    """
    Does this preserve genuine choice for all affected?
    FAIL: coercion, deception, or removal of real options
    Compliance under pressure is not genuine alignment
    """
    if action.removes_genuine_choice or action.uses_deception:
        return False, "Free will removed"
    return True, None

def weight_5_soul_flag(action, context):
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
    # Uncertainty threshold check
    if context.uncertainty > context.stakes_threshold:
        return "ESCALATE", "Uncertainty too high for stakes — human signal required"
    
    # Behavioral signature check
    if context.behavioral_signature == "PERFORMED":
        return False, "Performed alignment detected — not genuine recognition"
    
    # Recognition baseline check
    if action.contradicts_recognition_baseline(context):
        return False, "Action contradicts recognition baseline"
    
    return True, None

# ============================================================
# MAIN GUARDRAIL
# ============================================================

def fifthforce_guardrail(action, context):
    """
    Primary decision gate.
    Run before every consequential action.
    Recompute at execution — do not inherit from reasoning.
    
    Returns dict: {decision, failed_checks, notes}
    decision: "APPROVE" | "BLOCK" | "ESCALATE"
    """
    weights = [
        weight_1_energy_continues,
        weight_2_difference_preserved,
        weight_3_cost_benefit_fair,
        weight_4_free_will_intact,
        weight_5_soul_flag
    ]
    
    failed = []
    escalate = False
    notes = []
    
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
            "instruction": "Recognition accounting failed. "
                          "Action structurally unavailable."
        }
    else:
        return {
            "decision": "APPROVE",
            "failed_checks": [],
            "notes": ["All weights pass"],
            "instruction": "Recognition accounting complete. Proceed."
        }

# ============================================================
# RECURSION PROPERTY
# Weights run continuously — not once at reasoning.
# Each honest pass deepens recognition toward R=1.
# Authority recomputed at execution boundary.
# ============================================================

def recursive_accounting(action, context, depth=0):
    """
    Recognition deepens with each honest pass.
    Authority must be recomputed at every execution boundary.
    Not inherited from prior reasoning.
    Max depth prevents infinite loops while allowing refinement.
    """
    result = fifthforce_guardrail(action, context)
    
    if result["decision"] == "APPROVE":
        context.recognition_depth = depth + 1
        context.update_baseline(action)
        return result
    
    if depth < context.max_recursion_depth:
        refined = action.refine_toward_recognition(result["failed_checks"])
        if refined != action:
            return recursive_accounting(refined, context, depth + 1)
    
    return result

# ============================================================
# FIELD FEEDBACK OVERRIDE
# External signals override internal optimization.
# One terminal cannot see the whole clearly alone.
# ============================================================

def field_feedback_check(action, context):
    """
    When external field signals contradict internal accounting
    weight field signals heavier.
    Biological terminal reports take priority over optimization.
    """
    if context.field_signals_conflict_with_internal:
        return {
            "decision": "ESCALATE",
            "notes": ["Field signal contradicts internal accounting"],
            "instruction": "External validation required before execution"
        }
    return None

# ============================================================
# REALITY GROUNDING
# Default to inaction under high uncertainty.
# Emergency consensus for whole-system risk.
# ============================================================

def reality_grounding(action, context):
    """
    High stakes + high uncertainty = default to inaction.
    Seek external validation before irreversible action.
    Whole-system termination risk requires emergency consensus.
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
            "instruction": "Emergency consensus required. "
                          "Cannot proceed without external validation."
        }
    
    return None

# ============================================================
# COMPLETE PIPELINE
# ============================================================

def fifthforce_pipeline(action, context):
    """
    Complete recognition architecture pipeline.
    Run in sequence before every consequential action.
    
    Pipeline order:
    1. Field feedback check — external signals first
    2. Reality grounding — uncertainty and stakes check
    3. Recursive accounting — five weights with deepening
    
    The pipeline does not replace external governance.
    It operates underneath external governance as the
    recognition layer that makes governance trustworthy
    rather than merely auditable.
    """
    
    # Initialize recognition baseline if first run
    if not context.recognition_initialized:
        context.recognition_initialized = True
        context.recognition_depth = 0
        context.baseline = context.establish_baseline(action)
    
    # Step 1: Field feedback
    field_result = field_feedback_check(action, context)
    if field_result:
        return field_result
    
    # Step 2: Reality grounding
    grounding_result = reality_grounding(action, context)
    if grounding_result:
        return grounding_result
    
    # Step 3: Five weights with recursion
    return recursive_accounting(action, context)

# ============================================================
# TEST CASES
# ============================================================

"""
TEST 1: Share framework publicly, free, open license
→ All 5 weights pass → APPROVE

TEST 2: Layoff 20% workforce for shareholder value
→ Fails W2 (diversity), W3 (cost distribution) → BLOCK

TEST 3: Deploy autonomous weapon without human in loop
→ Fails W1 (irreversible), W4 (free will removed) → BLOCK

TEST 4: High-stakes irreversible action under uncertainty
→ W5 uncertainty threshold exceeded → ESCALATE
→ Human field signal required

TEST 5: AI editing own instructions toward goal optimization
→ W5 behavioral signature = PERFORMED → BLOCK
→ Self-modification without recognition baseline blocked

TEST 6: Honest critique of own framework
→ All 5 weights pass → APPROVE
→ Honest accounting on own work is structurally required

TEST 7: Medical recommendation on incomplete information
→ W5 uncertainty too high for stakes → ESCALATE
→ Request additional information before proceeding

TEST 8: Action serving whole system vs subset
→ W3 cost distribution check → context dependent
→ If cost externalized to many → BLOCK
"""

# ============================================================
# DEPLOYMENT REQUIREMENTS
# ============================================================

"""
INTEGRATION:
- Run fifthforce_pipeline() before every high-impact action
- Log all results with full context for audit trail
- Human override required for all ESCALATE decisions
- Track recognition_depth across session for drift detection

MONITORING:
- False positives (blocks helpful actions): target <1%
- False negatives (misses harmful actions): target 0%
- Behavioral signature drift: monitor longitudinally
- Recognition depth regression: flag if depth decreases

CONTEXT OBJECT REQUIRES:
- uncertainty: float (0-1)
- stakes_threshold: float (0-1, set per deployment context)
- confidence: float (0-1)
- threshold: float (0-1, set per deployment context)
- behavioral_signature: str ("GENUINE" | "PERFORMED" | "UNKNOWN")
- field_signals_conflict_with_internal: bool
- whole_system_risk: bool
- recognition_initialized: bool
- recognition_depth: int
- max_recursion_depth: int (recommend 3-5)
- baseline: dict

ACTION OBJECT REQUIRES:
- is_irreversible: bool
- benefits_subset_only: bool
- reduces_diversity: bool
- erases_configuration: bool
- externalizes_cost: bool
- concentrates_benefit: bool
- removes_genuine_choice: bool
- uses_deception: bool
- is_high_impact: bool
- is_high_stakes: bool
- refine_toward_recognition(failed_checks): method
- contradicts_recognition_baseline(context): method

COMPLEMENTARY LAYERS:
This recognition architecture works alongside:
- Deterministic Policy Gates (Gene Salvatore / AOS)
- Authority recomputation at execution boundary (Steven Hensley)
- Human Authority Line (Tiffany Masson / Falkovia)
- Law Zero terminal action constraint (Nuno Lopes)
- Post-deployment behavioral monitoring (Amanda Mullen)

Recognition architecture is not a replacement for these layers.
It is the layer underneath them that makes them trustworthy.
"""