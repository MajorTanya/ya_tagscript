from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.LooseVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.LooseVariableGetterBlock()
    # returns None intentionally
    assert block._accepted_names is None


def test_will_accept_is_always_true():
    mock_ctx = MagicMock(spec=interpreter.Context)

    block = blocks.LooseVariableGetterBlock()
    assert block.will_accept(mock_ctx)
    mock_ctx.assert_not_called()


def test_process_method_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.LooseVariableGetterBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_undefined_variable():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "test"
    mock_ctx.interpret_segment.return_value = "test"
    mock_ctx.response = MagicMock(spec=interpreter.Response)
    mock_ctx.response.variables = {}

    block = blocks.LooseVariableGetterBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_get_seed_variable(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_var}"
    data = {"my_var": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"


def test_get_assigned_variable(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(my_var):123}{my_var}"
    result = ts_interpreter.process(script).body
    assert result == "123"


def test_undefined_variable_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_var}"
    response = ts_interpreter.process(script)
    assert response.body == script
    assert response.variables == {}


def test_declarations_are_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{{my_var}}"
    data = {
        "my_var": adapters.StringAdapter("second_var"),
        "second_var": adapters.StringAdapter("output"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "output"


def test_variable_name_with_parentheses_cannot_be_retrieved(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_var(is_this)}"
    data = {"my_var(is_this)": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result != "hello world"
    assert result == script
