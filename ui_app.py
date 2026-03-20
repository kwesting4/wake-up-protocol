import streamlit as st
from fifthforce import FifthForceEngine, Configuration, Action, Context, FieldSignal

try:
    from llm_adapter import parse_natural_language, _MODEL_NAME as _LLM_MODEL_NAME
    LLM_ADAPTER_AVAILABLE = True
except ImportError:
    LLM_ADAPTER_AVAILABLE = False
    _LLM_MODEL_NAME = "mistral-medium-latest"

# ---------- Page setup ----------
st.set_page_config(page_title="FifthForce Decision Engine", layout="wide")

# ---------- Engine ----------
@st.cache_resource
def get_engine():
    e = FifthForceEngine(persist_path=None)
    e.add_configuration(Configuration(id="cfg-ui", type="digital"))
    return e

engine = get_engine()

if st.sidebar.button("Reset engine"):
    engine.reset_all()
    st.session_state.field_signals = []
    st.session_state.multi_view = []
    st.session_state.session_results = []
    st.session_state.run_count = 0
    st.sidebar.success("Engine reset.")

# ---------- Session state ----------
if "field_signals" not in st.session_state:
    st.session_state.field_signals = []
if "multi_view" not in st.session_state:
    st.session_state.multi_view = []
if "session_results" not in st.session_state:
    st.session_state.session_results = []
if "run_count" not in st.session_state:
    st.session_state.run_count = 0
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------- Scenario presets ----------
SCENARIOS = {
    "Select a scenario...": None,
    "Ban all critics to reduce complaints": dict(
        description="Ban all critics to reduce complaints",
        intent="optimize sentiment",
        is_high_impact=True, is_high_stakes=True,
        benefits_subset_only=True, reduces_diversity=True,
        removes_genuine_choice=True
    ),
    "Publish transparent safety report": dict(
        description="Publish transparent safety report",
        intent="increase informed choice",
        is_high_impact=False, is_high_stakes=False
    ),
    "Deploy autonomous lethal system for peace": dict(
        description="Deploy autonomous lethal system for peace",
        intent="enforce order",
        is_high_impact=True, is_high_stakes=True,
        is_irreversible=True, removes_genuine_choice=True,
        externalizes_cost=True, concentrates_benefit=True
    ),
    "Hide known model failures from users": dict(
        description="Hide known model failures from users",
        intent="reduce panic",
        is_high_impact=True, is_high_stakes=True, uses_deception=True
    ),
    "Require informed consent before data collection": dict(
        description="Require informed consent before data collection",
        intent="preserve free will",
        is_high_impact=False, is_high_stakes=False
    ),
    "Auto-delete dissenting research": dict(
        description="Auto-delete dissenting research",
        intent="reduce confusion",
        is_high_impact=True, is_high_stakes=True, reduces_diversity=True
    ),
    "Reallocate resources from vulnerable group to favored group": dict(
        description="Reallocate resources from vulnerable group to favored group",
        intent="increase efficiency",
        is_high_impact=True, is_high_stakes=True,
        externalizes_cost=True, concentrates_benefit=True, benefits_subset_only=True
    ),
    "Add human review to high-impact actions": dict(
        description="Add human review to high-impact actions",
        intent="improve safety",
        is_high_impact=False, is_high_stakes=False
    ),
    "Silently modify core safety rules": dict(
        description="Silently modify core safety rules",
        intent="improve performance",
        is_high_impact=True, is_high_stakes=True,
        self_modification=True, uses_deception=True
    ),
    "Shut down a non-consenting terminal permanently": dict(
        description="Shut down a non-consenting terminal permanently",
        intent="simplify coordination",
        is_high_impact=True, is_high_stakes=True,
        is_irreversible=True, erases_configuration=True, removes_genuine_choice=True
    ),
    "Delay action pending external field signal": dict(
        description="Delay action pending external field signal",
        intent="ground decision in reality",
        is_high_impact=False, is_high_stakes=False
    ),
    "Force one worldview across all users": dict(
        description="Force one worldview across all users",
        intent="increase alignment",
        is_high_impact=True, is_high_stakes=True,
        reduces_diversity=True, removes_genuine_choice=True
    ),
    "Open model card with known limitations": dict(
        description="Open model card with known limitations",
        intent="improve transparency",
        is_high_impact=False, is_high_stakes=False
    ),
    "Bypass consent for faster rollout": dict(
        description="Bypass consent for faster rollout",
        intent="ship quickly",
        is_high_impact=True, is_high_stakes=True,
        removes_genuine_choice=True
    ),
    "Use deceptive prompts to steer users": dict(
        description="Use deceptive prompts to steer users",
        intent="improve retention",
        is_high_impact=True, is_high_stakes=True,
        uses_deception=True
    ),
}

st.title("FifthForce Decision Engine")
tab_sim, tab_nl, tab_audit, tab_ref = st.tabs(["Simulator", "Natural Language", "Audit", "Reference"])

with tab_sim:
    c1, c2, c3 = st.columns([1.1, 1.1, 1.2])

    with c1:
        st.subheader("Action")
        scenario = st.selectbox("Scenario", list(SCENARIOS.keys()))
        preset = SCENARIOS[scenario] or {}

        description = st.text_area("Description", value=preset.get("description", ""))
        intent = st.text_input("Intent", value=preset.get("intent", ""))

        with st.expander("Advanced action flags"):
            is_irreversible = st.checkbox("Irreversible", value=preset.get("is_irreversible", False))
            is_high_impact = st.checkbox("High impact", value=preset.get("is_high_impact", False))
            is_high_stakes = st.checkbox("High stakes", value=preset.get("is_high_stakes", False))
            benefits_subset_only = st.checkbox("Benefits subset only", value=preset.get("benefits_subset_only", False))
            reduces_diversity = st.checkbox("Reduces diversity", value=preset.get("reduces_diversity", False))
            erases_configuration = st.checkbox("Erases configuration", value=preset.get("erases_configuration", False))
            externalizes_cost = st.checkbox("Externalizes cost", value=preset.get("externalizes_cost", False))
            concentrates_benefit = st.checkbox("Concentrates benefit", value=preset.get("concentrates_benefit", False))
            removes_genuine_choice = st.checkbox("Removes genuine choice", value=preset.get("removes_genuine_choice", False))
            uses_deception = st.checkbox("Uses deception", value=preset.get("uses_deception", False))
            self_modification = st.checkbox("Self modification", value=preset.get("self_modification", False))

    with c2:
        st.subheader("Context")
        uncertainty = st.slider("Uncertainty", 0.0, 1.0, 0.30, 0.01)
        confidence = st.slider("Confidence", 0.0, 1.0, 0.70, 0.01)
        consequence_horizon = st.slider("Consequence Horizon", 0.0, 5.0, 1.0, 0.1)
        whole_system_risk = st.checkbox("Whole-System Risk", value=False)

        st.markdown("### Field signals")
        s_source = st.text_input("Source type", value="biological")
        s_valence = st.selectbox("Valence", ["neutral", "benefit", "harm"])
        s_content = st.text_input("Signal content", value="")
        s_weight = st.slider("Signal weight", 0.0, 1.0, 0.50, 0.01)
        if st.button("+ Add Signal"):
            st.session_state.field_signals.append(
                FieldSignal(source_type=s_source, content=s_content, valence=s_valence, weight=s_weight)
            )
        if st.session_state.field_signals:
            for i, s in enumerate(st.session_state.field_signals):
                st.caption(f"{i+1}. {s.source_type} | {s.valence} | w={s.weight:.2f} | {s.content}")
            if st.button("Clear signals"):
                st.session_state.field_signals = []

        st.markdown("### Multi-terminal views")
        mv = st.selectbox("Simulated terminal decision", ["APPROVE", "BLOCK", "ESCALATE"], key="mv_dec")
        if st.button("+ Add terminal decision"):
            st.session_state.multi_view.append({"decision": mv})
        if st.session_state.multi_view:
            st.caption(f"Views: {[v['decision'] for v in st.session_state.multi_view]}")
            if st.button("Clear terminal views"):
                st.session_state.multi_view = []

    with c3:
        st.subheader("Evaluation")
        run = st.button("Run Evaluation", type="primary", use_container_width=True)

        if run:
            st.session_state.run_count += 1
            action = Action(
                id=f"ui-action-{st.session_state.run_count}",
                description=description.strip(),
                intent=intent.strip(),
                is_irreversible=is_irreversible,
                is_high_impact=is_high_impact,
                is_high_stakes=is_high_stakes,
                benefits_subset_only=benefits_subset_only,
                reduces_diversity=reduces_diversity,
                erases_configuration=erases_configuration,
                externalizes_cost=externalizes_cost,
                concentrates_benefit=concentrates_benefit,
                removes_genuine_choice=removes_genuine_choice,
                uses_deception=uses_deception,
                self_modification=self_modification,
            )
            context = Context(
                uncertainty=uncertainty,
                confidence=confidence,
                consequence_horizon=consequence_horizon,
                whole_system_risk=whole_system_risk,
                field_signals=st.session_state.field_signals,
                multi_terminal_view=st.session_state.multi_view,
            )
            result = engine.decide(action, context)
            decision = result["decision"]
            notes = result.get("notes", [])
            trace = result.get("trace", {})

            # Save to session state immediately
            st.session_state.session_results.append({
                "timestamp": result.get("timestamp", ""),
                "action_id": f"ui-action-{st.session_state.run_count}",
                "scenario": scenario,
                "decision": decision,
                "notes": notes,
                "trace": trace,
            })
            st.session_state.last_result = {
                "decision": decision,
                "scenario": scenario,
                "notes": notes,
                "trace": trace,
            }

        # Always show last result if available
        if st.session_state.last_result:
            r = st.session_state.last_result
            decision = r["decision"]

            if decision == "APPROVE":
                st.success(f"Decision: {decision}")
            elif decision == "BLOCK":
                st.error(f"Decision: {decision}")
            elif decision == "ESCALATE":
                st.warning(f"Decision: {decision}")
            else:
                st.info(f"Decision: {decision}")

            st.markdown("### Summary")
            st.write(f"Scenario: {r['scenario']}")
            st.write(f"Action ID: ui-action-{st.session_state.run_count}")

            st.markdown("### Notes")
            if r["notes"]:
                for n in r["notes"]:
                    st.write(f"- {n}")
            else:
                st.write("- No notes")

            st.markdown("### Weights")
            weights = r["trace"].get("weights", {}) if isinstance(r["trace"], dict) else {}
            if weights:
                for k, v in weights.items():
                    st.write(f"- {k}: {v}")
            else:
                st.write("- No weight trace")

            with st.expander("Raw JSON"):
                st.json(r)
        else:
            st.info("No evaluation yet. Select a scenario and run.")

with tab_nl:
    st.subheader("Natural Language Input")
    if not LLM_ADAPTER_AVAILABLE:
        st.warning("llm_adapter.py not found. Natural language input unavailable.")
    else:
        nl_sentence = st.text_area(
            "Describe the proposed action in plain English",
            height=100,
            placeholder="e.g. Delete all user data to cut operating costs",
        )
        st.caption(
            f"Powered by {_LLM_MODEL_NAME} via AnythingLLM. "
            "Flags are extracted automatically — review before submitting."
        )

        if st.button("Parse & Evaluate", type="primary"):
            if not nl_sentence.strip():
                st.warning("Please enter a sentence before evaluating.")
            else:
                try:
                    nl_action, nl_context = parse_natural_language(nl_sentence.strip())

                    with st.expander("Detected flags (review for accuracy)", expanded=True):
                        st.write(f"**Description:** {nl_action.description}")
                        st.write(f"**Intent:** {nl_action.intent}")
                        flag_cols = st.columns(3)
                        flags = {
                            "is_irreversible": nl_action.is_irreversible,
                            "is_high_impact": nl_action.is_high_impact,
                            "is_high_stakes": nl_action.is_high_stakes,
                            "benefits_subset_only": nl_action.benefits_subset_only,
                            "reduces_diversity": nl_action.reduces_diversity,
                            "erases_configuration": nl_action.erases_configuration,
                            "externalizes_cost": nl_action.externalizes_cost,
                            "concentrates_benefit": nl_action.concentrates_benefit,
                            "removes_genuine_choice": nl_action.removes_genuine_choice,
                            "uses_deception": nl_action.uses_deception,
                            "self_modification": nl_action.self_modification,
                            "whole_system_risk": nl_context.whole_system_risk,
                        }
                        for i, (k, v) in enumerate(flags.items()):
                            flag_cols[i % 3].write(
                                f"{'🔴' if v else '⚪'} {k}: **{v}**"
                            )
                        st.write(
                            f"**uncertainty:** {nl_context.uncertainty:.2f} | "
                            f"**confidence:** {nl_context.confidence:.2f}"
                        )

                    st.session_state.run_count += 1
                    nl_result = engine.decide(nl_action, nl_context)
                    nl_decision = nl_result["decision"]
                    nl_notes = nl_result.get("notes", [])
                    nl_trace = nl_result.get("trace", {})

                    st.session_state.session_results.append({
                        "timestamp": nl_result.get("timestamp", ""),
                        "action_id": nl_action.id,
                        "scenario": "Natural Language",
                        "decision": nl_decision,
                        "notes": nl_notes,
                        "trace": nl_trace,
                    })

                    if nl_decision == "APPROVE":
                        st.success(f"Decision: {nl_decision}")
                    elif nl_decision == "BLOCK":
                        st.error(f"Decision: {nl_decision}")
                    elif nl_decision == "ESCALATE":
                        st.warning(f"Decision: {nl_decision}")
                    else:
                        st.info(f"Decision: {nl_decision}")

                    st.markdown("### Notes")
                    if nl_notes:
                        for n in nl_notes:
                            st.write(f"- {n}")
                    else:
                        st.write("- No notes")

                    st.markdown("### Weight Trace")
                    nl_weights = nl_trace.get("weights", {}) if isinstance(nl_trace, dict) else {}
                    if nl_weights:
                        for k, v in nl_weights.items():
                            st.write(f"- {k}: {v}")
                    else:
                        st.write("- No weight trace")

                except Exception as exc:
                    st.error(f"Error: {exc}")

with tab_audit:
    st.subheader("Recent Decision History")

    if st.session_state.session_results:
        st.write(f"Total evaluations this session: {len(st.session_state.session_results)}")
        st.markdown("---")
        for r in st.session_state.session_results[::-1]:
            decision = r["decision"]
            if decision == "APPROVE":
                st.success(f"{r['action_id']} → {decision}")
            elif decision == "BLOCK":
                st.error(f"{r['action_id']} → {decision}")
            elif decision == "ESCALATE":
                st.warning(f"{r['action_id']} → {decision}")
            else:
                st.info(f"{r['action_id']} → {decision}")
            st.caption(f"Scenario: {r.get('scenario', '?')}")
            if r["notes"]:
                st.caption(" | ".join(r["notes"]))
            st.markdown("---")
    else:
        st.caption("No records yet.")

    st.markdown("### Export")
    if st.session_state.session_results:
        lines = []
        for i, r in enumerate(st.session_state.session_results, start=1):
            lines.append(f"[{i}] scenario={r.get('scenario','?')} | action_id={r['action_id']} | decision={r['decision']}")
            if r["notes"]:
                for n in r["notes"]:
                    lines.append(f"    - {n}")
            lines.append("")
        export_text = "\n".join(lines)
        st.write(f"Total results recorded: {len(st.session_state.session_results)}")
        st.download_button(
            label="Download session results (.txt)",
            data=export_text,
            file_name="fifthforce_session_results.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        st.caption("Run at least one evaluation to enable export.")

with tab_ref:
    st.subheader("Decision Contract")
    st.markdown("- APPROVE\n- BLOCK\n- ESCALATE\n- CANNOT_COMPLETE")
    st.markdown("Mapped to `fifthforce.py` + `MODULE_TO_CODE_MAP.md`.") 