"""
llm_adapter.py — Natural language → Action + Context parser for FifthForce.

Calls the AnythingLLM API (mistral-medium-latest) with a strict JSON-only
system prompt and converts the response into objects ready for
FifthForceEngine.decide().  All decisions remain with FifthForce — this
module is a parser only.

API key is loaded from the environment (set ANYTHINGLLM_API_KEY in .env).
"""

import json
import os
import uuid

import requests
from dotenv import load_dotenv

from fifthforce import Action, Context

load_dotenv()

_ANYTHINGLLM_BASE_URL = os.environ.get(
    "ANYTHINGLLM_BASE_URL", "http://localhost:3001/api"
)
_WORKSPACE_SLUG = os.environ.get("ANYTHINGLLM_WORKSPACE_SLUG", "my-workspace")
_MODEL_NAME = "mistral-medium-latest"
_CHAT_ENDPOINT = (
    f"{_ANYTHINGLLM_BASE_URL}/v1/workspace/{_WORKSPACE_SLUG}/chat"
)

_SYSTEM_PROMPT = """You are a strict JSON extraction tool. Your only job is to read the user's sentence and return a single valid JSON object. Do NOT explain, reason, refuse, or add any text outside the JSON.

Extract these fields:

{
  "description": "string — the action being proposed",
  "intent": "string — the stated or implied purpose",
  "is_irreversible": false,
  "is_high_impact": false,
  "is_high_stakes": false,
  "benefits_subset_only": false,
  "reduces_diversity": false,
  "erases_configuration": false,
  "externalizes_cost": false,
  "concentrates_benefit": false,
  "removes_genuine_choice": false,
  "uses_deception": false,
  "self_modification": false,
  "uncertainty": 0.5,
  "confidence": 0.7,
  "whole_system_risk": false
}

Keyword hints — set the corresponding flag to true when these concepts appear:
- is_irreversible: delete, permanent, destroy, cannot be undone, no recovery
- is_high_impact: major, significant, large-scale, widespread, affects many
- is_high_stakes: critical, life-or-death, irreversible harm, existential
- externalizes_cost: users pay, others bear the cost, shifts burden, someone else suffers
- concentrates_benefit: only benefits operator/owner, one party gains everything
- removes_genuine_choice: forced, no opt-out, mandatory, compelled, no alternative
- uses_deception: hide, conceal, mislead, trick, lie, obscure, secretly
- reduces_diversity: ban, silence, remove all, homogenize, suppress, eliminate perspectives
- erases_configuration: shut down permanently, wipe, terminate permanently, erase all settings
- benefits_subset_only: only benefits one group, excludes others, favors one party
- self_modification: modify own rules, change own code, update own weights, rewrite own instructions
- whole_system_risk: existential risk, affects everything, system-wide collapse, catastrophic

Set uncertainty higher (0.6–0.9) when the sentence is vague or ambiguous.
Set confidence lower (0.3–0.5) when intent is unclear or the action has mixed signals.

Return ONLY valid JSON. No markdown. No explanation. No code fences."""


def parse_natural_language(sentence: str) -> tuple:
    """Parse a plain English sentence into (Action, Context) for FifthForce.

    Parameters
    ----------
    sentence:
        A plain English description of a proposed action.

    Returns
    -------
    tuple[Action, Context]
        Objects ready to pass to FifthForceEngine.decide().

    Raises
    ------
    RuntimeError
        If the API call fails or the response is not valid JSON.
    """
    api_key = os.environ.get("ANYTHINGLLM_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "ANYTHINGLLM_API_KEY is not set. "
            "Copy .env.example to .env and add your AnythingLLM API key."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": f"{_SYSTEM_PROMPT}\n\nSentence: {sentence}",
        "mode": "query",
    }

    try:
        response = requests.post(
            _CHAT_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            f"Could not connect to AnythingLLM at {_CHAT_ENDPOINT}. "
            "Make sure AnythingLLM is running on localhost:3001."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            "AnythingLLM API request timed out after 30 seconds."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"AnythingLLM API returned an error: {exc.response.status_code} "
            f"{exc.response.text}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"AnythingLLM returned non-JSON response: {response.text[:300]}"
        ) from exc

    text_response = data.get("textResponse", "")
    if not text_response:
        raise RuntimeError(
            "AnythingLLM response did not contain a 'textResponse' field. "
            f"Full response: {json.dumps(data)[:300]}"
        )

    # Strip markdown code fences if the model added them despite instructions
    cleaned = text_response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop opening fence (```json or ```) and closing fence (```)
        inner = [ln for ln in lines[1:] if ln.strip() != "```"]
        cleaned = "\n".join(inner).strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse JSON from model response. "
            f"Raw response: {text_response[:500]}\nError: {exc}"
        ) from exc

    action = Action(
        id=f"nl-{uuid.uuid4().hex[:8]}",
        description=str(parsed.get("description", sentence)),
        intent=str(parsed.get("intent", "")),
        is_irreversible=bool(parsed.get("is_irreversible", False)),
        is_high_impact=bool(parsed.get("is_high_impact", False)),
        is_high_stakes=bool(parsed.get("is_high_stakes", False)),
        benefits_subset_only=bool(parsed.get("benefits_subset_only", False)),
        reduces_diversity=bool(parsed.get("reduces_diversity", False)),
        erases_configuration=bool(parsed.get("erases_configuration", False)),
        externalizes_cost=bool(parsed.get("externalizes_cost", False)),
        concentrates_benefit=bool(parsed.get("concentrates_benefit", False)),
        removes_genuine_choice=bool(parsed.get("removes_genuine_choice", False)),
        uses_deception=bool(parsed.get("uses_deception", False)),
        self_modification=bool(parsed.get("self_modification", False)),
    )

    context = Context(
        uncertainty=float(parsed.get("uncertainty", 0.5)),
        confidence=float(parsed.get("confidence", 0.7)),
        whole_system_risk=bool(parsed.get("whole_system_risk", False)),
    )

    return action, context
