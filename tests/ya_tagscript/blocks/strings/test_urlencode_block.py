from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.URLEncodeBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.URLEncodeBlock()
    assert block._accepted_names == {"urlencode"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.URLEncodeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_urlencode_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urlencode:covid-19 sucks}"
    result = ts_interpreter.process(script).body
    assert result == "covid-19%20sucks"


def test_dec_urlencode_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urlencode(+):im stuck at home writing docs}"
    result = ts_interpreter.process(script).body
    assert result == "im+stuck+at+home+writing+docs"


def test_dec_urlencode_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "<https://ya-tagscript.readthedocs.io/en/latest/search.html?q={urlencode(+):{args}}&check_keywords=yes&area=default>"
    data = {"args": adapters.StringAdapter("command block")}
    result = ts_interpreter.process(script, data).body
    assert (
        result
        == "<https://ya-tagscript.readthedocs.io/en/latest/search.html?q=command+block&check_keywords=yes&area=default>"
    )


def test_dec_urlencode_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urlencode:{my_var}}"
    data = {"my_var": adapters.StringAdapter("test text")}
    result = ts_interpreter.process(script, data).body
    assert result == "test%20text"


def test_dec_urlencode_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{urlencode({my_var}):hello world}"
    data = {"my_var": adapters.StringAdapter("+")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello+world"
