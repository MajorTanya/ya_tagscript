from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StopBlock(),
        blocks.StrictVariableGetterBlock(),
        blocks.CommandBlock(),
    ]
    return TagScriptInterpreter(b)


@pytest.fixture
def ts_interpreter_with_all_block():
    b = [
        blocks.StopBlock(),
        blocks.StrictVariableGetterBlock(),
        blocks.CommandBlock(),
        blocks.AllBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.StopBlock()
    assert block._accepted_names == {"stop", "halt", "error"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.StopBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.StopBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.StopBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_stop_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{stop({args}==):You must provide arguments for this tag.}"
    data = {"args": adapters.StringAdapter("")}
    result = ts_interpreter.process(script, data).body
    assert result == "You must provide arguments for this tag."


def test_dec_stop_missing_payload_is_allowed(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{stop(1==1)}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_stop_parsing_continues_on_false_condition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{stop(1==2):You must provide arguments for this tag.}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_stop_parsing_is_stopped_immediately(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{stop({args}==):You must provide arguments for this tag.}"
        + "{cmd:my unreachable command}"
    )
    data = {"args": adapters.StringAdapter("")}
    response = ts_interpreter.process(script, data)
    assert response.body == "You must provide arguments for this tag."
    assert response.actions.get("commands") is None


def test_dec_stop_parsing_only_stops_on_stop_block(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{cmd:a reachable command}"
        + "{stop({args}==):You must provide arguments for this tag.}"
        + "{cmd:my unreachable command}"
    )
    data = {"args": adapters.StringAdapter("")}
    response = ts_interpreter.process(script, data)
    assert response.body == "You must provide arguments for this tag."
    assert response.actions.get("commands") == ["a reachable command"]


def test_dec_stop_message_replaces_entire_output(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Hello there. {stop(true):STOPPED} General Kenobi."
    result = ts_interpreter.process(script).body
    assert result == "STOPPED"


def test_dec_stop_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Hello {stop({my_var}==1)} there"
    data = {"my_var": adapters.IntAdapter(1)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_dec_stop_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "hello {stop(this!=that):{my_var}} you"
    data = {"my_var": adapters.StringAdapter("broken")}
    result = ts_interpreter.process(script, data).body
    assert result == "broken"


def test_dec_stop_nested_block_as_parameter_is_interpreted(
    ts_interpreter_with_all_block: TagScriptInterpreter,
):
    script = "hello {stop({all(1==1|{args}==):true|false}):{my_var}} you"
    data = {
        "args": adapters.StringAdapter(""),
        "my_var": adapters.StringAdapter("broken"),
    }
    result = ts_interpreter_with_all_block.process(script, data).body
    assert result == "broken"
