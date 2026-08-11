import pytest
from pydantic import ValidationError

from app.modules.assistant.infrastructure.agents.langchain_agent_orchestrator import (
    AgentDecision,
)


def test_decision_schema_does_not_contain_open_tool_payload_object() -> None:
    schema = AgentDecision.model_json_schema()

    payload_schema = schema["properties"]["tool_payload_json"]
    branches = payload_schema["anyOf"]

    assert all(branch.get("type") != "object" for branch in branches)


def test_decision_parses_tool_payload_json_object() -> None:
    decision = AgentDecision(
        action="tool_call",
        final_answer="",
        tool_name="search",
        tool_payload_json='{"query": "FastAPI", "limit": 3}',
    )

    assert decision.parse_tool_payload() == {"query": "FastAPI", "limit": 3}


def test_decision_uses_empty_payload_when_json_is_absent() -> None:
    decision = AgentDecision(
        action="respond",
        final_answer="Done",
        tool_name="",
        tool_payload_json=None,
    )

    assert decision.parse_tool_payload() == {}


@pytest.mark.parametrize("payload_json", ["not-json", "[]", '"text"'])
def test_decision_rejects_invalid_or_non_object_payload(payload_json: str) -> None:
    decision = AgentDecision(
        action="tool_call",
        final_answer="",
        tool_name="search",
        tool_payload_json=payload_json,
    )

    with pytest.raises(ValidationError):
        decision.parse_tool_payload()