from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.BreakBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.BreakBlock()
    assert block._accepted_names == {"break", "shortcircuit", "short"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.BreakBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_break_missing_payload_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break(1==1)}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_break_empty_parameter(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break():Broken}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_break_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break({args}==):You did not provide any input.}"
    data = {"args": adapters.StringAdapter("")}
    result = ts_interpreter.process(script, data).body
    assert result == "You did not provide any input."


def test_dec_break_docs_example_one_else_case(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break({args}==):You did not provide any input.}"
    data = {"args": adapters.StringAdapter("some args")}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_dec_break_empty_parameter_returns_empty(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break():This is a break}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_break_falsy_parameter_returns_empty(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{break(1==2):This is a break}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_break_message_replaces_entire_output(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Hello there. {break(true):BREAK} General Kenobi."
    result = ts_interpreter.process(script).body
    assert result == "BREAK"


def test_dec_break_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Hello {break({my_var}==1)} there"
    data = {"my_var": adapters.IntAdapter(1)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_dec_break_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "hello {break(this!=that):{my_var}} you"
    data = {"my_var": adapters.StringAdapter("broken")}
    result = ts_interpreter.process(script, data).body
    assert result == "broken"
