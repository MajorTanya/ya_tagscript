from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.PythonBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.PythonBlock()
    assert block._accepted_names == {"contains", "in", "index"}


def test_process_method_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.PythonBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_invalid_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "something else"
    mock_ctx.node.parameter = "something else"
    mock_ctx.node.payload = "something else"

    block = blocks.PythonBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "contains"  # valid to pass first check
    mock_ctx.node.parameter = None

    block = blocks.PythonBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "contains"  # valid to pass first check
    mock_ctx.node.parameter = ""  # valid to pass second check
    mock_ctx.node.payload = None

    block = blocks.PythonBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_contains_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{contains(mute):How does it feel to be muted?}"
    result = ts_interpreter.process(script).body
    assert result == "false"


def test_dec_contains_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{contains(muted?):How does it feel to be muted?}"
    result = ts_interpreter.process(script).body
    assert result == "true"


def test_dec_in_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{in(apple pie):banana pie apple pie and other pie}"
    result = ts_interpreter.process(script).body
    assert result == "true"


def test_dec_in_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{in(mute):How does it feel to be muted?}"
    result = ts_interpreter.process(script).body
    assert result == "true"


def test_dec_in_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{in(a):How does it feel to be muted?}"
    result = ts_interpreter.process(script).body
    assert result == "false"


def test_dec_index_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{index(food.):I love to eat food. everyone does.}"
    result = ts_interpreter.process(script).body
    assert result == "4"


def test_dec_index_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{index(pie):I love to eat food. everyone does.}"
    result = ts_interpreter.process(script).body
    assert result == "-1"


def test_dec_contains_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{contains({my_var}):hello world}"
    data = {"my_var": adapters.StringAdapter("hello")}
    result = ts_interpreter.process(script, data).body
    assert result == "true"


def test_dec_contains_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{contains(hi):{my_var}}"
    data = {"my_var": adapters.StringAdapter("hi there")}
    result = ts_interpreter.process(script, data).body
    assert result == "true"


def test_dec_in_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{in({my_var}):hello world it's me}"
    data = {"my_var": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "true"


def test_dec_in_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{in(hi there):{my_var}}"
    data = {"my_var": adapters.StringAdapter("hi there neighbour")}
    result = ts_interpreter.process(script, data).body
    assert result == "true"


def test_dec_index_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{index({my_var}):hello world}"
    data = {"my_var": adapters.StringAdapter("hello")}
    result = ts_interpreter.process(script, data).body
    assert result == "0"


def test_dec_index_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{index(there):{my_var}}"
    data = {"my_var": adapters.StringAdapter("hi there")}
    result = ts_interpreter.process(script, data).body
    assert result == "1"
