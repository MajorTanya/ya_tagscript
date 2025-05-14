from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.URLDecodeBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.URLDecodeBlock()
    assert block._accepted_names == {"urldecode"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.URLDecodeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_urldecode_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode:hello%20world}"
    result = ts_interpreter.process(script).body
    assert result == "hello world"


def test_dec_urldecode_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode(+):Hello+there.+General+Kenobi.}"
    result = ts_interpreter.process(script).body
    assert result == "Hello there. General Kenobi."


def test_dec_urldecode_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode(+):this%20is+a%20combined+test}"
    result = ts_interpreter.process(script).body
    assert result == "this is a combined test"


def test_dec_urldecode_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode:this+will+keep+the+plus+signs}"
    result = ts_interpreter.process(script).body
    assert result == "this+will+keep+the+plus+signs"


def test_dec_urldecode_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode:{my_var}}"
    data = {"my_var": adapters.StringAdapter("test%20text")}
    result = ts_interpreter.process(script, data).body
    assert result == "test text"


def test_dec_urldecode_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urldecode({my_var}):hello+world}"
    data = {"my_var": adapters.StringAdapter("+")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"
