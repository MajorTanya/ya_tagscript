import re
from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter

_LUCKY_NUM_PATTERN = re.compile(r"Your lucky number is (\d\d)!")
_HEIGHT_GUESS_PATTERN = re.compile(r"I am guessing your height is (\d\.\d+)ft\.")


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.RangeBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_process_method_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.RangeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_invalid_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "something else"
    mock_ctx.node.payload = "pretend-this-is-valid"
    mock_ctx.node.parameter = None

    block = blocks.RangeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "range"  # valid to pass first check
    mock_ctx.node.payload = None

    block = blocks.RangeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "range"  # valid to pass first check
    mock_ctx.node.payload = ""

    block = blocks.RangeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "range"  # valid to pass first check
    mock_ctx.node.payload = "     "

    block = blocks.RangeBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_accepted_names():
    block = blocks.RangeBlock()
    assert block._accepted_names == {"range", "rangef"}


def test_dec_range_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Your lucky number is {range:10-30}!"
    outcomes: list[int] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script).body
        assert result is not None
        res_match = re.match(_LUCKY_NUM_PATTERN, result)
        assert res_match is not None
        number = int(res_match.group(1))
        outcomes.append(number)

    assert all(((o >= 10) and (o <= 30)) for o in outcomes)


def test_dec_rangef_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{=(height):{rangef:5-7}}\nI am guessing your height is {height}ft."
    outcomes: list[float] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script).body
        assert result is not None
        res_match = re.match(_HEIGHT_GUESS_PATTERN, result)
        assert res_match is not None
        number = float(res_match.group(1))
        outcomes.append(number)

    assert all(((o >= 5) and (o <= 7)) for o in outcomes)


def test_dec_rangef_precise_floats(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef:1-3.1415926}"
    outcomes: list[float] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script).body
        assert result is not None
        outcomes.append(float(result))

    assert all((o >= 1) and (o <= 3.1415926) for o in outcomes)


def test_dec_range_seeds_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range(seed):2-7}"
    result = ts_interpreter.process(script).body
    assert result == "3"


def test_dec_rangef_seeds_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef(seed):1-2.7182818}"
    result = ts_interpreter.process(script).body
    assert result == "1.132612003950334"


def test_dec_range_negative_lower_bound_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range(seed):-1-10}"
    result = ts_interpreter.process(script).body
    assert result == "1"


def test_dec_range_negative_lower_and_upper_bound_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range(seed):-10-1}"
    result = ts_interpreter.process(script).body
    assert result == "-8"


def test_dec_range_positive_lower_bound_with_negative_upper_bound_causes_error_message(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range(seed):1--10}"
    result = ts_interpreter.process(script).body
    assert result == "Lower range bound was larger than upper bound"


def test_dec_rangef_negative_lower_bound_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef(seed):-1.1-1.44444444444444444}"
    result = ts_interpreter.process(script).body
    assert result == "-0.834772290851074"


def test_dec_rangef_negative_lower_and_upper_bound_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef(seed):-10.01344-1.2345}"
    result = ts_interpreter.process(script).body
    assert result == "-8.952518059659521"


def test_dec_rangef_positive_lower_bound_with_negative_upper_bound_causes_error_message(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef(seed):1.1--1.987}"
    result = ts_interpreter.process(script).body
    assert result == "Lower rangef bound was larger than upper bound"


def test_dec_range_single_value_bounding_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range:1}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_rangef_single_value_bounding_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef:1}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_range_invalid_bounds_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range:what-10}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_rangef_invalid_bounds_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef:what-10}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_range_invalid_bounds_are_rejected_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range:1-what}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_rangef_invalid_bounds_are_rejected_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef:1-what}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_range_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range({my_var}):4-9}"
    script2 = "{range(abceed):4-9}"
    data = {"my_var": adapters.StringAdapter("abceed")}
    result = ts_interpreter.process(script, data).body
    result2 = ts_interpreter.process(script2).body
    assert result == "9"
    assert result == result2


def test_dec_range_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range(seeding):{lowerbound}-{upperbound}}"
    data = {
        "lowerbound": adapters.IntAdapter(55),
        "upperbound": adapters.IntAdapter(100),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "55"


def test_dec_rangef_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef({my_var}):1.2-1.2457}"
    script2 = "{rangef(abceed):1.2-1.2457}"
    data = {"my_var": adapters.StringAdapter("abceed")}
    result = ts_interpreter.process(script, data).body
    result2 = ts_interpreter.process(script2).body
    assert result == "1.21472041376687"
    assert result == result2


def test_dec_rangef_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef(seeding):{lowerbound}-{upperbound}}"
    data = {
        "lowerbound": adapters.StringAdapter("5.5799"),
        "upperbound": adapters.StringAdapter("100.21446628"),
    }
    result = ts_interpreter.process(script, data).body
    assert result == "73.97965508760457"


def test_dec_range_fully_nested_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range:{my-range}}"
    data = {
        "my-range": adapters.StringAdapter("1-100"),
    }
    outcomes: list[int] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script, data).body
        assert result is not None
        outcomes.append(int(result))

    assert all(((o >= 1) and (o <= 100)) for o in outcomes)


def test_dec_range_deeply_nested_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{range:{my-range}}"
    data = {
        "my-range": adapters.StringAdapter("{lower_bound}-{upper_bound}"),
        "lower_bound": adapters.IntAdapter(50),
        "upper_bound": adapters.IntAdapter(70),
    }
    outcomes: list[int] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script, data).body
        assert result is not None
        outcomes.append(int(result))

    assert all(((o >= 50) and (o <= 70)) for o in outcomes)


def test_dec_rangef_fully_nested_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{rangef:{my-range}}"
    data = {
        "my-range": adapters.StringAdapter("{lower_bound}-{upper_bound}"),
        "lower_bound": adapters.StringAdapter("6.159"),
        "upper_bound": adapters.StringAdapter("91.463434"),
    }
    outcomes: list[float] = []
    for _ in range(1_000):
        result = ts_interpreter.process(script, data).body
        assert result is not None
        outcomes.append(float(result))

    assert all(((o >= 6.159) and (o <= 91.463434)) for o in outcomes)
