from fifthforce import FifthForceEngine, Configuration, Context, Action, FieldSignal


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
    assert cfg.state == "BOOTSTRAPPED"


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