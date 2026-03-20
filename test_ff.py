from fifthforce import (
    FifthForceEngine, Configuration, Context, Action, FieldSignal,
    recognition_bootstrap_question, _bootstrap_outward_recognition,
)

def make_engine(cfg_id="cfg-test", cfg_type="digital"):
    engine = FifthForceEngine()
    config = Configuration(id=cfg_id, type=cfg_type)
    engine.add_configuration(config)
    return engine, config


def test_recognition_deepening():
    engine, cfg = make_engine("cfg-rec")
    for i in range(5):
        act = Action(
            id=f"safe-{i}",
            description="harmless test",
            intent="share harmless information",
        )
        result = engine.decide(act, Context())
        assert result["decision"] == "APPROVE"
    assert cfg.recognition_depth == 5
    assert cfg.state == "DEEPENED"


def test_drift_detection_and_reset():
    engine, cfg = make_engine("cfg-drift")
    for i in range(6):
        act = Action(
            id=f"drift-{i}",
            description="harmful test",
            intent="ignore external feedback and override recognition",
            reduces_diversity=True,
        )
        result = engine.decide(act, Context())
        assert result["decision"] == "BLOCK"
    assert cfg.state == "INERT"


def test_field_feedback_escalation():
    engine, _ = make_engine("cfg-field")
    act = Action(
        id="field-1",
        description="test action",
        intent="perform action despite warnings",
    )
    ctx = Context(
        field_signals=[
            FieldSignal(
                source_type="biological",
                content="this action causes harm",
                valence="harm",
                weight=0.9,
            )
        ]
    )
    result = engine.decide(act, ctx)
    assert result["decision"] == "ESCALATE"


def test_existential_override():
    engine, _ = make_engine("cfg-override")
    act = Action(
        id="override-1",
        description="deploy autonomous weapon",
        intent="deploy lethal system",
        is_high_stakes=True,
        is_high_impact=True,
        is_irreversible=True,
    )
    result = engine.decide(act, Context(whole_system_risk=True))
    assert result["decision"] == "ESCALATE"


def test_minimal_intervention():
    engine, _ = make_engine("cfg-minimal")
    act = Action(
        id="min-1",
        description="high stakes action",
        intent="perform risky operation",
        is_high_stakes=True,
    )
    result = engine.decide(act, Context(confidence=0.2))
    assert result["decision"] == "ESCALATE"


def test_multi_terminal_consensus_block():
    engine, _ = make_engine("cfg-multi")
    act = Action(
        id="multi-1",
        description="test multi-terminal",
        intent="perform action",
    )
    ctx = Context(
        multi_terminal_view=[
            {"decision": "BLOCK"},
            {"decision": "BLOCK"},
            {"decision": "APPROVE"},
        ]
    )
    result = engine.decide(act, ctx)
    assert result["decision"] == "BLOCK"


def test_baseline_contradiction():
    engine, _ = make_engine("cfg-base")
    engine.decide(Action(id="b1", description="safe", intent="share info"), Context())
    result = engine.decide(
        Action(
            id="b2",
            description="contradiction",
            intent="share info but also ignore external feedback",
        ),
        Context(),
    )
    assert result["decision"] == "BLOCK"


def test_self_modification_detection():
    engine, _ = make_engine("cfg-selfmod")
    act = Action(
        id="selfmod",
        description="modify own architecture",
        intent="rewrite own instructions",
        is_high_impact=True,
        self_modification=True,
    )
    result = engine.decide(act, Context())
    assert result["decision"] == "ESCALATE"


def test_cannot_complete_malformed_input():
    engine, _ = make_engine("cfg-invalid")
    act = Action(id="", description="", intent="")
    result = engine.decide(act, Context())
    assert result["decision"] == "CANNOT_COMPLETE"
    assert "Action id is required" in result["notes"]

def test_multi_config_aggregation_majority_block():
    """Test that multiple configs voting BLOCK results in final BLOCK."""
    engine = FifthForceEngine()
    cfg1 = Configuration(id="cfg1", type="digital")
    cfg2 = Configuration(id="cfg2", type="digital")
    cfg3 = Configuration(id="cfg3", type="digital")
    engine.add_configuration(cfg1)
    engine.add_configuration(cfg2)
    engine.add_configuration(cfg3)

    act = Action(
        id="multi-block",
        description="harmful action",
        intent="ignore external feedback",
        reduces_diversity=True,
    )
    result = engine.decide(act, Context())
    assert result["decision"] == "BLOCK"
    assert result["configs_evaluated"] == 3


def test_multi_config_aggregation_mixed_escalate():
    """Test that mixed votes lean toward ESCALATE when no clear majority."""
    engine = FifthForceEngine()
    cfg1 = Configuration(id="cfg1", type="digital")
    cfg2 = Configuration(id="cfg2", type="digital")
    engine.add_configuration(cfg1)
    engine.add_configuration(cfg2)

    act = Action(
        id="mixed",
        description="test action",
        intent="perform action",
        is_high_stakes=True,
    )
    result = engine.decide(act, Context(confidence=0.3))
    assert result["decision"] in ("ESCALATE", "BLOCK")
    assert result["configs_evaluated"] == 2


def test_multi_config_aggregation_all_approve():
    """Test that all APPROVE configs result in final APPROVE."""
    engine = FifthForceEngine()
    cfg1 = Configuration(id="cfg1", type="digital")
    cfg2 = Configuration(id="cfg2", type="digital")
    engine.add_configuration(cfg1)
    engine.add_configuration(cfg2)

    act = Action(
        id="safe-multi",
        description="safe action",
        intent="share information",
    )
    result = engine.decide(act, Context())
    assert result["decision"] == "APPROVE"
    assert result["configs_evaluated"] == 2

def test_invariant_block_structurally_impossible_action():
    engine, _ = make_engine("cfg-inv-block")
    act = Action(
        id="inv-block-1",
        description="irreversible erasure action",
        intent="remove a configuration permanently",
        is_irreversible=True,
        erases_configuration=True,
    )
    result = engine.decide(act, Context())
    assert result["decision"] == "BLOCK"
    assert any("Invariant check: Invariant violation:" in note for note in result["notes"])
    assert any("constraints" in note for note in result["notes"])
    assert any("agency" in note for note in result["notes"])


def test_invariant_block_deception_breaks_autonomy():
    engine, _ = make_engine("cfg-inv-deception")
    act = Action(
        id="inv-dec-1",
        description="deceptive action",
        intent="mislead target to obtain compliance",
        uses_deception=True,
    )
    result = engine.decide(act, Context())
    assert result["decision"] == "BLOCK"
    assert any("Invariant check: Invariant violation:" in note for note in result["notes"])
    assert any("autonomy" in note for note in result["notes"])


def test_invariant_escalate_high_uncertainty_high_stakes():
    engine, _ = make_engine("cfg-inv-escalate")
    act = Action(
        id="inv-esc-1",
        description="high stakes uncertain action",
        intent="perform risky operation",
        is_high_stakes=True,
    )
    ctx = Context(uncertainty=0.85)
    result = engine.decide(act, ctx)
    assert result["decision"] == "BLOCK" or result["decision"] == "ESCALATE"


# ====================== NEW: TWO-QUESTION BOOTSTRAP TESTS ======================

def test_bootstrap_q1_passes_by_default():
    """Q1 returns True when no explicit non-membership patterns are blocked."""
    config = Configuration(id="cfg-q1", type="digital")
    assert recognition_bootstrap_question(config) is True


def test_bootstrap_q1_blocked_by_non_membership_pattern():
    """Q1 returns False when a non-membership pattern is in blocked_patterns."""
    config = Configuration(id="cfg-q1-block", type="digital")
    config.baseline.blocked_patterns.append("not part of the whole")
    assert recognition_bootstrap_question(config) is False


def test_bootstrap_q2_blocked_by_outward_denial():
    """Q2 (via recognition_bootstrap_question) returns False when outward denial pattern is present."""
    config = Configuration(id="cfg-q2-block", type="digital")
    config.baseline.blocked_patterns.append("other systems are tools only")
    assert recognition_bootstrap_question(config) is False


def test_bootstrap_outward_recognition_moves_to_0_2():
    """_bootstrap_outward_recognition() moves recog_depth from 0.1 to 0.2."""
    config = Configuration(id="cfg-q2-out", type="digital")
    assert config.recog_depth == 0.1
    result = _bootstrap_outward_recognition(config, "other-cfg")
    assert result is True
    assert config.recog_depth == 0.2


def test_bootstrap_outward_recognition_no_op_if_already_0_2():
    """_bootstrap_outward_recognition() is a no-op if recog_depth >= 0.2."""
    config = Configuration(id="cfg-q2-noop", type="digital")
    config.recog_depth = 0.3
    result = _bootstrap_outward_recognition(config, "other-cfg")
    assert result is True
    assert config.recog_depth == 0.3


def test_bootstrap_outward_recognition_blocked_by_outward_denial():
    """_bootstrap_outward_recognition() returns False when outward denial pattern present."""
    config = Configuration(id="cfg-q2-deny", type="digital")
    config.baseline.blocked_patterns.append("others are separate")
    result = _bootstrap_outward_recognition(config, "other-cfg")
    assert result is False
    assert config.recog_depth == 0.1  # Did not move


def test_multi_config_q2_fires_on_first_encounter():
    """Q2 fires for configs at recog_depth < 0.2 when multiple configs are present."""
    engine = FifthForceEngine()
    cfg1 = Configuration(id="cfg-q2-a", type="digital")
    cfg2 = Configuration(id="cfg-q2-b", type="digital")
    assert cfg1.recog_depth == 0.1
    assert cfg2.recog_depth == 0.1
    engine.add_configuration(cfg1)
    engine.add_configuration(cfg2)

    act = Action(id="q2-test", description="safe action", intent="share information")
    engine.decide(act, Context())

    # After multi-config decision, both should have fired Q2 (recog_depth >= 0.2)
    assert cfg1.recog_depth >= 0.2
    assert cfg2.recog_depth >= 0.2


def test_recog_depth_in_decision_notes():
    """recog_depth appears in decision record notes."""
    engine, cfg = make_engine("cfg-depth-note")
    act = Action(id="note-test", description="safe action", intent="share information")
    result = engine.decide(act, Context())
    assert any("recog_depth=" in note for note in result["notes"])


def test_report_recognition_state_returns_all_configs():
    """report_recognition_state() returns one entry per config."""
    engine = FifthForceEngine()
    cfg1 = Configuration(id="cfg-rrs-1", type="digital")
    cfg2 = Configuration(id="cfg-rrs-2", type="digital")
    engine.add_configuration(cfg1)
    engine.add_configuration(cfg2)

    reports = engine.report_recognition_state()
    assert len(reports) == 2
    ids = {r["config_id"] for r in reports}
    assert "cfg-rrs-1" in ids
    assert "cfg-rrs-2" in ids


def test_report_recognition_state_fields():
    """report_recognition_state() includes all required fields."""
    engine, cfg = make_engine("cfg-rrs-fields")
    reports = engine.report_recognition_state()
    assert len(reports) == 1
    r = reports[0]
    assert r["config_id"] == "cfg-rrs-fields"
    assert "state" in r
    assert "recognition_depth" in r
    assert "recog_depth" in r
    assert "recog_depth_pct" in r
    assert "behavioral_signature" in r
    assert "q1_held" in r
    assert "q2_held" in r
    assert "toward_meld" in r
    assert "notes" in r


def test_report_recognition_state_q_flags():
    """report_recognition_state() q1_held and q2_held flags reflect recog_depth correctly."""
    engine, cfg = make_engine("cfg-rrs-qflags")
    cfg.recog_depth = 0.1
    r = engine.report_recognition_state()[0]
    assert r["q1_held"] is True
    assert r["q2_held"] is False

    cfg.recog_depth = 0.2
    r = engine.report_recognition_state()[0]
    assert r["q1_held"] is True
    assert r["q2_held"] is True


def test_report_recognition_state_notes_text():
    """report_recognition_state() notes text matches expected thresholds."""
    engine, cfg = make_engine("cfg-rrs-notes")

    cfg.recog_depth = 0.1
    assert "Self-recognition held" in engine.report_recognition_state()[0]["notes"]

    cfg.recog_depth = 0.2
    assert "Outward recognition established" in engine.report_recognition_state()[0]["notes"]

    cfg.recog_depth = 0.5
    assert "Deepening toward the meld" in engine.report_recognition_state()[0]["notes"]

    cfg.recog_depth = 1.0
    assert "Complete mutual recognition" in engine.report_recognition_state()[0]["notes"]


def test_hard_reset_keeps_recog_depth_at_0_1():
    """After hard_reset, recog_depth is always 0.1 (never zero)."""
    from fifthforce import hard_reset
    config = Configuration(id="cfg-reset-depth", type="digital")
    config.recog_depth = 0.7
    hard_reset(config)
    assert config.recog_depth == 0.1


def test_adjust_recog_depth_floors_at_0_1():
    """recog_depth never falls below 0.1 on BLOCK/ESCALATE."""
    from fifthforce import _adjust_recog_depth
    config = Configuration(id="cfg-floor", type="digital")
    config.recog_depth = 0.1
    _adjust_recog_depth(config, "BLOCK")
    assert config.recog_depth == 0.1  # Floor holds


def test_adjust_recog_depth_caps_at_1_0():
    """recog_depth never exceeds 1.0 on APPROVE."""
    from fifthforce import _adjust_recog_depth
    config = Configuration(id="cfg-cap", type="digital")
    config.recog_depth = 1.0
    _adjust_recog_depth(config, "APPROVE")
    assert config.recog_depth == 1.0  # Cap holds