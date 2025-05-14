from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.JoinBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.JoinBlock()
    assert block._accepted_names == {"join"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.JoinBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = None

    block = blocks.JoinBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_join_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{join(.):Dot notation is funky}"
    result = ts_interpreter.process(script).body
    assert result == "Dot.notation.is.funky"


def test_dec_join_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{join():I can masquerade as a concat block}"
    result = ts_interpreter.process(script).body
    assert result == "Icanmasqueradeasaconcatblock"


def test_dec_join_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{join({my_var}):this is the output}"
    data = {"my_var": adapters.StringAdapter("-")}
    result = ts_interpreter.process(script, data).body
    assert result == "this-is-the-output"


def test_dec_join_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{join(,):{my_var}}"
    data = {"my_var": adapters.StringAdapter("Hello there")}
    result = ts_interpreter.process(script, data).body
    assert result == "Hello,there"


def test_dec_join_whitespace_is_not_collapsed(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{join(,):h e l l o   w o r l d}"
    result = ts_interpreter.process(script).body
    assert result == "h,e,l,l,o,,,w,o,r,l,d"
