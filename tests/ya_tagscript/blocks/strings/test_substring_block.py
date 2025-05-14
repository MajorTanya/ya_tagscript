from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.SubstringBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.SubstringBlock()
    assert block._accepted_names == {"substring", "substr"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = None

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = ""

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "valid to pass first check"
    mock_ctx.node.payload = "     "

    block = blocks.SubstringBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_substring_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(1-4):testing}"
    result = ts_interpreter.process(script).body
    assert result == "est"


def test_dec_substring_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(6):hello world}"
    result = ts_interpreter.process(script).body
    assert result == "world"


def test_dec_substring_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(100):hello world}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_substring_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(-100):hello world}"
    result = ts_interpreter.process(script).body
    assert result == "hello world"


def test_dec_substring_inclusive_start_no_end(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(2):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == "23456789"


def test_dec_substring_inclusive_start_exclusive_end(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(2-5):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == "234"


def test_dec_substring_negative_start_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(-2):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == "89"


def test_dec_substring_negative_start_and_end_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(-5--2):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == "567"


def test_dec_substring_invalid_index_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(xyz):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_substring_too_large_index_returns_empty_string_like_normal_string_slice(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(1000):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_substring_too_large_negative_index_returns_full_string_like_normal_string_slice(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(-1000):0123456789}"
    result = ts_interpreter.process(script).body
    assert result == "0123456789"


def test_dec_substring_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring({my_var}):0123456789}"
    data = {"my_var": adapters.IntAdapter(6)}
    result = ts_interpreter.process(script, data).body
    assert result == "6789"


def test_dec_substring_parameter_range_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring({my_var}):0123456789}"
    data = {"my_var": adapters.StringAdapter("1-3")}
    result = ts_interpreter.process(script, data).body
    assert result == "12"


def test_dec_substring_partial_parameter_range_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring({first_var}{second_var}):0123456789}"
    data = {
        "first_var": adapters.IntAdapter(4),
        "second_var": adapters.StringAdapter("-8"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "4567"


def test_dec_substring_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring(1-8):{my_var}}"
    data = {"my_var": adapters.StringAdapter("0123456789")}
    result = ts_interpreter.process(script, data).body
    assert result == "1234567"


def test_dec_substring_both_parameter_and_payload_are_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{substring({first_param}-{second_param}):{payload_var}}"
    data = {
        "first_param": adapters.IntAdapter(2),
        "second_param": adapters.IntAdapter(9),
        "payload_var": adapters.StringAdapter("0123456789"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "2345678"
