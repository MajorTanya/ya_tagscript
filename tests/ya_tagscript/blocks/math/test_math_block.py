import math
from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.MathBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


# Note: These test expressions have been generated randomly to cover a wide spread
# of possible operation combinations. Their sensibility is irrelevant.
# ---
# All results are checked to the currently configured precision (15 at this time).
# Importantly, sgn/trunc/no-arg round all return ints, not floats, so they do not have
# _any_ decimals in their results.
# ---
# - 001-110 test random combinations of operator/functions
# - 111-141 test each individual operator/function/constant in an isolated manner
# - 142-147 test multi-arg round expressions to their correct number of decimals
# - 148-149: test support for literal π expressions (instead of transliterated 'pi')
# - 150-151: test support for literal τ expressions (instead of transliterated 'tau')


def test_accepted_names():
    block = blocks.MathBlock()
    assert block._accepted_names == {"math", "m", "+", "calc"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.MathBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = ""

    block = blocks.MathBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = "     "

    block = blocks.MathBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_math_invalid_identifier_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:pi * gamma}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_math_overflowing_calculation_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:100 ^ 100 ^ 100}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_math_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:{my_var} ^ 3}"
    data = {"my_var": adapters.IntAdapter(3)}
    result = ts_interpreter.process(script, data).body
    assert result == "27.0"


def test_dec_math_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:1 + 2 * 3}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:pi * 2}"
    result = ts_interpreter.process(script).body
    assert result == "6.283185307179586"


def test_dec_math_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(10 / 3, 2)}"
    result = ts_interpreter.process(script).body
    assert result == "3.33"


# region 001-110: 110 random expressions, tested with the 'math' declaration


def test_dec_math_expr_001(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 + 3}"
    result = ts_interpreter.process(script).body
    assert result == "8.0"


def test_dec_math_expr_002(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 - 4}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_003(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:7 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "14.0"


def test_dec_math_expr_004(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:8 / 2}"
    result = ts_interpreter.process(script).body
    assert result == "4.0"


def test_dec_math_expr_005(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 ^ 3}"
    result = ts_interpreter.process(script).body
    assert result == "125.0"


def test_dec_math_expr_006(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:9 % 4}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_007(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(pi / 2)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_008(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_009(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tan(pi / 4)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_010(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sinh(0)}"
    result = ts_interpreter.process(script).body
    assert result == "0.0"


def test_dec_math_expr_011(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cosh(0)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_012(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tanh(1)}"
    result = ts_interpreter.process(script).body
    assert result == "0.761594155955765"


def test_dec_math_expr_013(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(2)}"
    result = ts_interpreter.process(script).body
    assert result == "7.38905609893065"


def test_dec_math_expr_014(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:abs(-7)}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_015(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:trunc(3.78)}"
    result = ts_interpreter.process(script).body
    assert result == "3"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_016(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(4.56)}"
    result = ts_interpreter.process(script).body
    assert result == "5"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_017(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sgn(-10)}"
    result = ts_interpreter.process(script).body
    assert result == "-1"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_018(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(1000)}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_019(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:ln(e^2)}"
    result = ts_interpreter.process(script).body
    assert result == "2.0"


def test_dec_math_expr_020(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log2(16)}"
    result = ts_interpreter.process(script).body
    assert result == "4.0"


def test_dec_math_expr_021(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sqrt(25)}"
    result = ts_interpreter.process(script).body
    assert result == "5.0"


def test_dec_math_expr_022(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:e ^ 1}"
    result = ts_interpreter.process(script).body
    assert result == "2.718281828459045"


def test_dec_math_expr_023(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:pi * 2}"
    result = ts_interpreter.process(script).body
    assert result == "6.283185307179586"


def test_dec_math_expr_024(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 += 5}"
    result = ts_interpreter.process(script).body
    assert result == "15.0"


def test_dec_math_expr_025(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:20 -= 3}"
    result = ts_interpreter.process(script).body
    assert result == "17.0"


def test_dec_math_expr_026(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:6 *= 2}"
    result = ts_interpreter.process(script).body
    assert result == "12.0"


def test_dec_math_expr_027(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:18 /= 3}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_028(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:(-3) ^ 2}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_029(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 - (-2)}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_030(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:+8}"
    result = ts_interpreter.process(script).body
    assert result == "8.0"


def test_dec_math_expr_031(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 / 3}"
    result = ts_interpreter.process(script).body
    assert result == "3.333333333333333"


def test_dec_math_expr_032(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:-sqrt(49)}"
    result = ts_interpreter.process(script).body
    assert result == "-7.0"


def test_dec_math_expr_033(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(pi)}"
    result = ts_interpreter.process(script).body
    assert result == "-1.0"


def test_dec_math_expr_034(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(-pi / 2)}"
    result = ts_interpreter.process(script).body
    assert result == "-1.0"


def test_dec_math_expr_035(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tanh(0.5)}"
    result = ts_interpreter.process(script).body
    assert result == "0.46211715726001"


def test_dec_math_expr_036(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(0.1)}"
    result = ts_interpreter.process(script).body
    assert result == "-1.0"


def test_dec_math_expr_037(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:ln(1)}"
    result = ts_interpreter.process(script).body
    assert result == "0.0"


def test_dec_math_expr_038(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sgn(0)}"
    result = ts_interpreter.process(script).body
    assert result == "0"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_039(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:trunc(-4.98)}"
    result = ts_interpreter.process(script).body
    assert result == "-4"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_040(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(-3.5)}"
    result = ts_interpreter.process(script).body
    assert result == "-4"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_041(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 + 3 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "11.0"


def test_dec_math_expr_042(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:(10 - 4) / 2}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_043(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:8 / 2 + 6}"
    result = ts_interpreter.process(script).body
    assert result == "10.0"


def test_dec_math_expr_044(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:7 * 2 - 5}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_045(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 ^ 2 - 3}"
    result = ts_interpreter.process(script).body
    assert result == "22.0"


def test_dec_math_expr_046(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:9 % 4 + 6}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_047(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(pi / 4) * sqrt(2)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_048(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0) + tan(pi / 4)}"
    result = ts_interpreter.process(script).body
    assert result == "2.0"


def test_dec_math_expr_049(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sinh(1) + cosh(1) - 1}"
    result = ts_interpreter.process(script).body
    assert result == "1.718281828459045"


def test_dec_math_expr_050(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(2) - ln(e^3) + 1}"
    result = ts_interpreter.process(script).body
    assert result == "5.38905609893065"


def test_dec_math_expr_051(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:abs(-7) + trunc(3.78) - 2}"
    result = ts_interpreter.process(script).body
    assert result == "8.0"


def test_dec_math_expr_052(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(4.56) + sgn(-10) + 2}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_053(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(1000) + log2(16) - log(100)}"
    result = ts_interpreter.process(script).body
    assert result == "5.0"


def test_dec_math_expr_054(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sqrt(25) + 3 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "11.0"


def test_dec_math_expr_055(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:e ^ 1 + pi - 4}"
    result = ts_interpreter.process(script).body
    assert result == "1.859874482048838"


def test_dec_math_expr_056(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 += 5 - 3}"
    result = ts_interpreter.process(script).body
    assert result == "12.0"


def test_dec_math_expr_057(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:20 -= 3 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "14.0"


def test_dec_math_expr_058(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:6 *= 2 + 1}"
    result = ts_interpreter.process(script).body
    assert result == "18.0"


def test_dec_math_expr_059(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:18 /= 3 - 1}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_060(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:(-3) ^ 2 + 4}"
    result = ts_interpreter.process(script).body
    assert result == "13.0"


def test_dec_math_expr_061(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 - (-2) + 7}"
    result = ts_interpreter.process(script).body
    assert result == "14.0"


def test_dec_math_expr_062(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 / 2 + 3 - 1}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_063(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:-sqrt(49) + 5 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_064(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(pi) + sin(-pi / 2) + 2}"
    result = ts_interpreter.process(script).body
    assert result == "0.0"


def test_dec_math_expr_065(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tanh(0.5) + sinh(1) - cosh(1)}"
    result = ts_interpreter.process(script).body
    assert result == "0.094237716088567"


def test_dec_math_expr_066(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(0.1) + ln(1) + 4}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_067(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sgn(-8) + trunc(-4.98) + 5}"
    result = ts_interpreter.process(script).body
    assert result == "0.0"


def test_dec_math_expr_068(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(-3.5) + sqrt(16) - 2}"
    result = ts_interpreter.process(script).body
    assert result == "-2.0"


def test_dec_math_expr_069(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(1) + ln(e) - pi}"
    result = ts_interpreter.process(script).body
    assert result == "0.576689174869252"


def test_dec_math_expr_070(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0) + tanh(1) * 2}"
    result = ts_interpreter.process(script).body
    assert result == "2.52318831191153"


def test_dec_math_expr_071(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 + 3 * 2 - 4 / 2}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_072(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:(10 - 4) / 2 + 7 * 3}"
    result = ts_interpreter.process(script).body
    assert result == "24.0"


def test_dec_math_expr_073(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:8 / 2 + 6 - 3 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "4.0"


def test_dec_math_expr_074(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:7 * 2 - 5 + 4 / 2}"
    result = ts_interpreter.process(script).body
    assert result == "11.0"


def test_dec_math_expr_075(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 ^ 2 - 3 + sqrt(16)}"
    result = ts_interpreter.process(script).body
    assert result == "26.0"


def test_dec_math_expr_076(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:9 % 4 + 6 - 2 * 3}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_077(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(pi / 4) * sqrt(2) + cos(0)}"
    result = ts_interpreter.process(script).body
    assert result == "2.0"


def test_dec_math_expr_078(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0) + tan(pi / 4) * 2 - 1}"
    result = ts_interpreter.process(script).body
    assert result == "2.0"


def test_dec_math_expr_079(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sinh(1) + cosh(1) - 1 + tanh(0.5)}"
    result = ts_interpreter.process(script).body
    assert result == "2.180398985719055"


def test_dec_math_expr_080(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(2) - ln(e^3) + 1 - log(10)}"
    result = ts_interpreter.process(script).body
    assert result == "4.38905609893065"


def test_dec_math_expr_081(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:abs(-7) + trunc(3.78) - 2 + round(4.56)}"
    result = ts_interpreter.process(script).body
    assert result == "13.0"


def test_dec_math_expr_082(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(4.56) + sgn(-10) + 2 - sqrt(9)}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_083(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(1000) + log2(16) - log(100) + 2}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_084(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sqrt(25) + 3 * 2 - 4 / 2}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_085(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:e ^ 1 + pi - 4 + ln(e^2)}"
    result = ts_interpreter.process(script).body
    assert result == "3.859874482048838"


def test_dec_math_expr_086(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 += 5 - 3 * 2 + 4}"
    result = ts_interpreter.process(script).body
    assert result == "13.0"


def test_dec_math_expr_087(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:20 -= 3 * 2 + sqrt(9) - 1}"
    result = ts_interpreter.process(script).body
    assert result == "12.0"


def test_dec_math_expr_088(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:6 *= 2 + 1 - 4 / 2}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_089(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:18 /= 3 - 1 + 5 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "1.5"


def test_dec_math_expr_090(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:(-3) ^ 2 + 4 - sqrt(16) + log2(32)}"
    result = ts_interpreter.process(script).body
    assert result == "14.0"


def test_dec_math_expr_091(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:5 - (-2) + 7 - 3 * 2}"
    result = ts_interpreter.process(script).body
    assert result == "8.0"


def test_dec_math_expr_092(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 / 2 + 3 - 1 * 5 + 4}"
    result = ts_interpreter.process(script).body
    assert result == "7.0"


def test_dec_math_expr_093(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:-sqrt(49) + 5 * 2 - log(100)}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_094(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(pi) + sin(-pi / 2) + 2 * 3 - 1}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_095(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tanh(0.5) + sinh(1) - cosh(1) + log(10)}"
    result = ts_interpreter.process(script).body
    assert result == "1.094237716088567"


def test_dec_math_expr_096(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(0.1) + ln(1) + 4 - sqrt(9) * 2}"
    result = ts_interpreter.process(script).body
    assert result == "-3.0"


def test_dec_math_expr_097(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sgn(-8) + trunc(-4.98) + 5 - round(2.6)}"
    result = ts_interpreter.process(script).body
    assert result == "-3.0"


def test_dec_math_expr_098(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(-3.5) + sqrt(16) - 2 * 3 + 10}"
    result = ts_interpreter.process(script).body
    assert result == "4.0"


def test_dec_math_expr_099(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(1) + ln(e) - pi + sqrt(9)}"
    result = ts_interpreter.process(script).body
    assert result == "3.576689174869252"


def test_dec_math_expr_100(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0) + tanh(1) * 2 - sqrt(4) + log2(8)}"
    result = ts_interpreter.process(script).body
    assert result == "3.52318831191153"


def test_dec_math_expr_101(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(6, 8) + sqrt(25)}"
    result = ts_interpreter.process(script).body
    assert result == "15.0"


def test_dec_math_expr_102(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log2(hypot(8, 15)) * round(3.5678, 2)}"
    result = ts_interpreter.process(script).body
    assert result == "14.59224234326371"


def test_dec_math_expr_103(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(7, 24) - tan(pi / 4) + 2}"
    result = ts_interpreter.process(script).body
    assert result == "26.0"


def test_dec_math_expr_104(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:abs(-hypot(9, 40)) + trunc(5.99)}"
    result = ts_interpreter.process(script).body
    assert result == "46.0"


def test_dec_math_expr_105(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(12, 16) / cos(0) + sinh(1)}"
    result = ts_interpreter.process(script).body
    assert result == "21.1752011936438"


def test_dec_math_expr_106(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tau / 2 + sin(tau / 4) * sqrt(49)}"
    result = ts_interpreter.process(script).body
    assert result == "10.141592653589793"


def test_dec_math_expr_107(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(10, tau) - log2(64) + cos(pi)}"
    result = ts_interpreter.process(script).body
    assert result == "4.810098120013967"


def test_dec_math_expr_108(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(1) * tau - round(3.1415, 2) + sinh(0)}"
    result = ts_interpreter.process(script).body
    assert result == "13.939468445347131"


def test_dec_math_expr_109(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tau ^ 2 / (hypot(3, 4) + log(100)) - 1}"
    result = ts_interpreter.process(script).body
    assert result == "4.639773943479633"


def test_dec_math_expr_110(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tau * cosh(1) - trunc(9.87) + abs(-5)}"
    result = ts_interpreter.process(script).body
    assert result == "5.695461572464488"


# endregion

# region 111-141: 31 single operator/function expressions, tested with 'math' declaration


def test_dec_math_expr_111_addition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:12 + 7}"
    result = ts_interpreter.process(script).body
    assert result == "19.0"


def test_dec_math_expr_112_subtraction(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:20 - 9}"
    result = ts_interpreter.process(script).body
    assert result == "11.0"


def test_dec_math_expr_113_multiplication(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:4 * 6}"
    result = ts_interpreter.process(script).body
    assert result == "24.0"


def test_dec_math_expr_114_division(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:18 / 3}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_115_i_addition(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:1 += 8}"
    result = ts_interpreter.process(script).body
    assert result == "9.0"


def test_dec_math_expr_116_i_subtraction(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:1 -= 6}"
    result = ts_interpreter.process(script).body
    assert result == "-5.0"


def test_dec_math_expr_117_i_multiplication(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:2 *= 5}"
    result = ts_interpreter.process(script).body
    assert result == "10.0"


def test_dec_math_expr_118_i_division(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:6 /= 2}"
    result = ts_interpreter.process(script).body
    assert result == "3.0"


def test_dec_math_expr_119_exponentiation(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:2 ^ 4}"
    result = ts_interpreter.process(script).body
    assert result == "16.0"


def test_dec_math_expr_120_modulo(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:15 % 7}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


def test_dec_math_expr_121_sine(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(4)}"
    result = ts_interpreter.process(script).body
    assert result == "-0.756802495307928"


def test_dec_math_expr_122_cosine(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(0.5)}"
    result = ts_interpreter.process(script).body
    assert result == "0.877582561890373"


def test_dec_math_expr_123_tangens(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tan(12)}"
    result = ts_interpreter.process(script).body
    assert result == "-0.635859928661581"


def test_dec_math_expr_124_hyperbolic_sine(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sinh(2)}"
    result = ts_interpreter.process(script).body
    assert result == "3.626860407847019"


def test_dec_math_expr_125_hyperbolic_cosine(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cosh(2)}"
    result = ts_interpreter.process(script).body
    assert result == "3.762195691083631"


def test_dec_math_expr_126_hyperbolic_tangens(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tanh(2)}"
    result = ts_interpreter.process(script).body
    assert result == "0.964027580075817"


def test_dec_math_expr_127_exponential_function(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:exp(3)}"
    result = ts_interpreter.process(script).body
    assert result == "20.085536923187668"


def test_dec_math_expr_128_absolute(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:abs(-12)}"
    result = ts_interpreter.process(script).body
    assert result == "12.0"


def test_dec_math_expr_129_truncation(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:trunc(9.99)}"
    result = ts_interpreter.process(script).body
    assert result == "9"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_130_no_arg_round(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(2.51)}"
    result = ts_interpreter.process(script).body
    assert result == "3"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_131_signum(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sgn(15)}"
    result = ts_interpreter.process(script).body
    assert result == "1"  # no-arg round/trunc/sgn return int not float


def test_dec_math_expr_132_log_base_10(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log(500)}"
    result = ts_interpreter.process(script).body
    assert result == "2.698970004336019"


def test_dec_math_expr_133_natural_log(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:ln(7.389)}"
    result = ts_interpreter.process(script).body
    assert result == "1.999992407806511"


def test_dec_math_expr_134_log_base_2(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:log2(32)}"
    result = ts_interpreter.process(script).body
    assert result == "5.0"


def test_dec_math_expr_135_sqrt(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sqrt(36)}"
    result = ts_interpreter.process(script).body
    assert result == "6.0"


def test_dec_math_expr_136_eulers_number(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:e}"
    result = ts_interpreter.process(script).body
    assert result == "2.718281828459045"
    assert result == str(round(math.e, 15))  # juuuust in case :)


def test_dec_math_expr_137_pi(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:pi}"
    result = ts_interpreter.process(script).body
    assert result == "3.141592653589793"
    assert result == str(round(math.pi, 15))  # juuuust in case :)


def test_dec_math_expr_138_tau(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tau}"
    result = ts_interpreter.process(script).body
    assert result == "6.283185307179586"
    assert result == str(round(math.tau, 15))  # juuuust in case :)


def test_dec_math_expr_139_unary_plus(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:+14}"
    result = ts_interpreter.process(script).body
    assert result == "14.0"


def test_dec_math_expr_140_unary_minus(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:-9}"
    result = ts_interpreter.process(script).body
    assert result == "-9.0"


def test_dec_math_expr_141_hypotenuse(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(3, 4)}"
    result = ts_interpreter.process(script).body
    assert result == "5.0"


# endregion

# region 142-147: 6 random multi-arg round expressions, tested with 'math' declaration


def test_dec_math_expr_142(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(3.141592, 1)}"
    result = ts_interpreter.process(script).body
    assert result == "3.1"


def test_dec_math_expr_143(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(9.87654, 3)}"
    result = ts_interpreter.process(script).body
    assert result == "9.877"


def test_dec_math_expr_144(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(27.4392, 2)}"
    result = ts_interpreter.process(script).body
    assert result == "27.44"


def test_dec_math_expr_145(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(0.987654, 4)}"
    result = ts_interpreter.process(script).body
    assert result == "0.9877"


def test_dec_math_expr_146(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(123.456789, 5)}"
    result = ts_interpreter.process(script).body
    assert result == "123.45679"


def test_dec_math_expr_147(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(12345, -2)}"
    result = ts_interpreter.process(script).body
    assert result == "12300.0"


# endregion

# region 148-149: 2 random literal π expressions, tested with 'math' declaration


def test_dec_math_expr_148(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:sin(π / 2) + sqrt(16)}"
    result = ts_interpreter.process(script).body
    assert result == "5.0"


def test_dec_math_expr_149(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:cos(π) * 2 + 3}"
    result = ts_interpreter.process(script).body
    assert result == "1.0"


# endregion

# region 150-151: 2 random literal τ expressions, tested with 'math' declaration


def test_dec_math_expr_150(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:tan(τ / 3) + log2(8)}"
    result = ts_interpreter.process(script).body
    assert result == "1.267949192431122"


def test_dec_math_expr_151(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:hypot(5, τ) - round(3.14, 1)}"
    result = ts_interpreter.process(script).body
    assert result == "4.929845428422482"


# endregion
