from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.ListBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.ListBlock()
    assert block._accepted_names == {"list"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.ListBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.ListBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.ListBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = None

    block = blocks.ListBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_list_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(1):apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == "banana"


def test_dec_list_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(-2):apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == "banana"


def test_dec_list_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(10):apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_list_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(0):{items}}"
    data = {
        "items": adapters.StringAdapter("1st~2nd~3rd"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "1st"


def test_dec_list_empty_parameter_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list():apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_list_bad_parameters_return_error(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(X):apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == "Could not parse list index"


def test_dec_list_float_parameters_return_error(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(1.5):apple~banana~secret third thing}"
    result = ts_interpreter.process(script).body
    assert result == "Could not parse list index"


def test_dec_list_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list({my_var}):first~second~third}"
    data = {"my_var": adapters.IntAdapter(1)}
    result = ts_interpreter.process(script, data).body
    assert result == "second"


def test_dec_list_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(0):{first}~{second}}"
    data = {
        "first": adapters.StringAdapter("one"),
        "second": adapters.StringAdapter("two"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "one"


def test_dec_list_nested_payload_is_interpreted_before_splitting(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{list(0):{items}}"
    data = {
        "items": adapters.StringAdapter("one~two~three"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "one"
