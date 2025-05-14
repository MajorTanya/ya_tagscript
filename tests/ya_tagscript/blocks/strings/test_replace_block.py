from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.ReplaceBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.ReplaceBlock()
    assert block._accepted_names == {"replace"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = None

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = ""

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = "     "

    block = blocks.ReplaceBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_replace_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(o,i):welcome to the server}"
    result = ts_interpreter.process(script).body
    assert result == "welcime ti the server"


def test_dec_replace_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(1,6):{args}}"
    data = {"args": adapters.StringAdapter("1234567")}
    result = ts_interpreter.process(script, data).body
    assert result == "6234567"


def test_dec_replace_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(, ):Test}"
    result = ts_interpreter.process(script).body
    assert result == "T e s t"


def test_dec_replace_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(an):An amazing Canadian banana}"
    result = ts_interpreter.process(script).body
    assert result == "An amazing Cadi ba"


def test_dec_replace_no_comma_means_remove(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(ee):Green tree bees see jeeps on freezing streets for weeks}"
    result = ts_interpreter.process(script).body
    assert result == "Grn tr bs s jps on frzing strts for wks"


def test_dec_replace_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace({my_var}):High five}"
    data = {"my_var": adapters.StringAdapter("i,x")}
    result = ts_interpreter.process(script, data).body
    assert result == "Hxgh fxve"


def test_dec_replace_split_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace({my_var},{other_var}):hello there}"
    data = {
        "my_var": adapters.StringAdapter("l"),
        "other_var": adapters.StringAdapter("q"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "heqqo there"


def test_dec_replace_nested_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace({my_var}):over the misty mountains}"
    data = {
        "my_var": adapters.StringAdapter("{first_var},{second_var}"),
        "first_var": adapters.StringAdapter("o"),
        "second_var": adapters.StringAdapter("a"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "aver the misty mauntains"


def test_dec_replace_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{replace(a,e):{my_var}}"
    data = {"my_var": adapters.StringAdapter("Half a tangerine")}
    result = ts_interpreter.process(script, data).body
    assert result == "Helf e tengerine"
