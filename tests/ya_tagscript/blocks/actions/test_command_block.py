from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.CommandBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.CommandBlock()
    assert block._accepted_names == {"c", "com", "cmd", "command"}


@pytest.mark.parametrize(
    "payload",
    (
        pytest.param(None, id="missing"),
        pytest.param("", id="empty"),
        pytest.param("    ", id="whitespace"),
    ),
)
def test_process_method_rejects_invalid_payloads(
    payload: str | None,
):
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = payload

    block = blocks.CommandBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_command_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command:ping}"
    response = ts_interpreter.process(script)
    assert response.actions.get("commands", []) == ["ping"]
    assert response.body == ""


def test_dec_command_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command:ban {target(id)} flooding/spam}"
    data = {"target": adapters.AttributeAdapter(MagicMock(id=42))}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    assert response.actions.get("commands", []) == ["ban 42 flooding/spam"]


def test_dec_command_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command:}"
    response = ts_interpreter.process(script)
    assert response.actions.get("commands") is None
    assert response.body == script


def test_dec_command_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command}"
    response = ts_interpreter.process(script)
    assert response.actions.get("commands") is None
    assert response.body == script


def test_dec_command_command_limit_is_enforced(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command:foo}{command:bar}{command:baz}{command:qux}"
    response = ts_interpreter.process(script)
    assert response.body == "`COMMAND LIMIT REACHED (3)`"


def test_dec_command_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{command:Hello {world}}"
    data = {"world": adapters.StringAdapter("everyone")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    commands = response.actions.get("commands", [])
    assert commands == ["Hello everyone"]
