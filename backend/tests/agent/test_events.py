import json

import pytest
from pydantic import TypeAdapter, ValidationError

from app.modules.agent.events import AgentEvent, TextChunkEvent, ToolResultEvent


def test_text_chunk_ascii_matches_legacy() -> None:
    item = "Hello world"
    legacy = f"data: {json.dumps({'type': 'token', 'content': item})}\n\n"
    new = TextChunkEvent(content=item).to_sse_data()
    assert new == legacy


def test_text_chunk_unicode_matches_legacy() -> None:
    item = "EXPLOSÃO!!! 你好 — ação"
    legacy = f"data: {json.dumps({'type': 'token', 'content': item})}\n\n"
    new = TextChunkEvent(content=item).to_sse_data()
    assert new == legacy


def test_text_chunk_double_quotes_matches_legacy() -> None:
    item = 'ele disse "olá" e saiu'
    legacy = f"data: {json.dumps({'type': 'token', 'content': item})}\n\n"
    new = TextChunkEvent(content=item).to_sse_data()
    assert new == legacy


def test_tool_result_matches_legacy() -> None:
    legacy_dict = {
        "type": "tool_call",
        "tool": "read_file",
        "args": {"path": "x.md"},
        "output": "Arquivo não encontrado",
        "status": "error",
    }
    legacy = f"data: {json.dumps(legacy_dict)}\n\n"
    new = ToolResultEvent(
        tool="read_file",
        args={"path": "x.md"},
        output="Arquivo não encontrado",
        status="error",
    ).to_sse_data()
    assert new == legacy


def test_tool_result_nested_args_matches_legacy() -> None:
    legacy_dict = {
        "type": "tool_call",
        "tool": "complex_tool",
        "args": {"outer": {"inner": [1, 2, 3]}},
        "output": "ok",
        "status": "ok",
    }
    legacy = f"data: {json.dumps(legacy_dict)}\n\n"
    new = ToolResultEvent(
        tool="complex_tool",
        args={"outer": {"inner": [1, 2, 3]}},
        output="ok",
        status="ok",
    ).to_sse_data()
    assert new == legacy


def test_agent_event_union_resolves_correct_type() -> None:
    adapter = TypeAdapter(AgentEvent)

    text_payload = {"type": "token", "content": "oi"}
    tool_payload = {
        "type": "tool_call",
        "tool": "read_file",
        "args": {},
        "output": "x",
        "status": "ok",
    }

    assert isinstance(adapter.validate_python(text_payload), TextChunkEvent)
    assert isinstance(adapter.validate_python(tool_payload), ToolResultEvent)


def test_tool_result_rejects_invalid_status() -> None:
    with pytest.raises(ValidationError):
        ToolResultEvent(
            tool="x",
            args={},
            output="y",
            status="OK",  # type: ignore[arg-type]  # maiúsculo — inválido por design
        )
