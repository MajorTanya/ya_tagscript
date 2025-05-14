from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.AssignmentBlock()
    assert block._accepted_names == {"=", "assign", "let", "var"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.AssignmentBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = None

    block = blocks.AssignmentBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_assign_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    script = "{assign(prefix):!}The prefix here is `{prefix}`."
    response = ts_interpreter.process(script)
    assert response.body == "The prefix here is `!`."
    prefix_adapter = response.variables.get("prefix")
    assert prefix_adapter is not None
    assert prefix_adapter.get_value(mock_ctx) == "!"


def test_dec_assign_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    script = "{assign(day):Monday}{if({day}==Wednesday):It's Wednesday my dudes!|The day is {day}.}"
    response = ts_interpreter.process(script)
    assert response.body == "The day is Monday."
    day_adapter = response.variables.get("day")
    assert day_adapter is not None
    assert day_adapter.get_value(mock_ctx) == "Monday"


def test_dec_assign_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{assign({my_var}):value}{xyz}"
    data = {"my_var": adapters.StringAdapter("xyz")}
    result = ts_interpreter.process(script, data).body
    assert result == "value"


def test_dec_assign_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{assign(xyz):{my_var}}{xyz}"
    data = {"my_var": adapters.StringAdapter("this value")}
    result = ts_interpreter.process(script, data).body
    assert result == "this value"


def test_dec_assign_recursion_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{assign(xyz):value}"
        "{assign(xyz):{xyz}|{xyz}}"
        "{assign(xyz):{xyz}|{xyz}}"
        "{assign(xyz):{xyz}|{xyz}}"
        "{xyz}"
    )
    result = ts_interpreter.process(script).body
    assert result == "value|value|value|value|value|value|value|value"
