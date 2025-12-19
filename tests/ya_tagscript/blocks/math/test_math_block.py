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


def test_dec_math_division_by_zero_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:10 / 0}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_math_invalid_syntax_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:round(100 K)}"
    result = ts_interpreter.process(script).body
    assert result == script


@pytest.mark.parametrize(
    ("expr", "out"),
    (
        pytest.param("SIn(4)", "-0.756802495307928", id="sine"),
        pytest.param("cOs(0.5)", "0.877582561890373", id="cosine"),
        pytest.param("TAN(12)", "-0.635859928661581", id="tangens"),
        pytest.param("sINH(2)", "3.626860407847019", id="hyperbolic_sine"),
        pytest.param("COSh(2)", "3.762195691083631", id="hyperbolic_cosine"),
        pytest.param("tAnH(2)", "0.964027580075817", id="hyperbolic_tangens"),
        pytest.param("exP(3)", "20.085536923187668", id="exponential_function"),
        pytest.param("abS(-12)", "12.0", id="absolute"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("trUNc(9.99)", "9", id="truncation"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("RoUnD(2.51)", "3", id="no_arg_round"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("SGn(15)", "1", id="signum"),
        pytest.param("LOg(500)", "2.698970004336019", id="log_base_10"),
        pytest.param("LN(7.389)", "1.999992407806511", id="natural_log"),
        pytest.param("lOG2(32)", "5.0", id="log_base_2"),
        pytest.param("SqRt(36)", "6.0", id="sqrt"),
    ),
)
def test_function_matching_is_case_insensitive(
    expr: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:" + expr + "}"
    result = ts_interpreter.process(script).body
    assert result == out


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
# - 148-151: test support for literal π/τ expressions (instead of transliterations)


# region 001-110: 110 random expressions, tested with the 'math' declaration


@pytest.mark.parametrize(
    ("expr", "out"),
    (
        pytest.param("5 + 3", "8.0", id="001"),
        pytest.param("10 - 4", "6.0", id="002"),
        pytest.param("7 * 2", "14.0", id="003"),
        pytest.param("8 / 2", "4.0", id="004"),
        pytest.param("5 ^ 3", "125.0", id="005"),
        pytest.param("9 % 4", "1.0", id="006"),
        pytest.param("sin(pi / 2)", "1.0", id="007"),
        pytest.param("cos(0)", "1.0", id="008"),
        pytest.param("tan(pi / 4)", "1.0", id="009"),
        pytest.param("sinh(0)", "0.0", id="010"),
        pytest.param("cosh(0)", "1.0", id="011"),
        pytest.param("tanh(1)", "0.761594155955765", id="012"),
        pytest.param("exp(2)", "7.38905609893065", id="013"),
        pytest.param("abs(-7)", "7.0", id="014"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("trunc(3.78)", "3", id="015"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("round(4.56)", "5", id="016"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("sgn(-10)", "-1", id="017"),
        pytest.param("log(1000)", "3.0", id="018"),
        pytest.param("ln(e^2)", "2.0", id="019"),
        pytest.param("log2(16)", "4.0", id="020"),
        pytest.param("sqrt(25)", "5.0", id="021"),
        pytest.param("e ^ 1", "2.718281828459045", id="022"),
        pytest.param("pi * 2", "6.283185307179586", id="023"),
        pytest.param("10 += 5", "15.0", id="024"),
        pytest.param("20 -= 3", "17.0", id="025"),
        pytest.param("6 *= 2", "12.0", id="026"),
        pytest.param("18 /= 3", "6.0", id="027"),
        pytest.param("(-3) ^ 2", "9.0", id="028"),
        pytest.param("5 - (-2)", "7.0", id="029"),
        pytest.param("+8", "8.0", id="030"),
        pytest.param("10 / 3", "3.333333333333333", id="031"),
        pytest.param("-sqrt(49)", "-7.0", id="032"),
        pytest.param("cos(pi)", "-1.0", id="033"),
        pytest.param("sin(-pi / 2)", "-1.0", id="034"),
        pytest.param("tanh(0.5)", "0.46211715726001", id="035"),
        pytest.param("log(0.1)", "-1.0", id="036"),
        pytest.param("ln(1)", "0.0", id="037"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("sgn(0)", "0", id="038"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("trunc(-4.98)", "-4", id="039"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("round(-3.5)", "-4", id="040"),
        pytest.param("5 + 3 * 2", "11.0", id="041"),
        pytest.param("(10 - 4) / 2", "3.0", id="042"),
        pytest.param("8 / 2 + 6", "10.0", id="043"),
        pytest.param("7 * 2 - 5", "9.0", id="044"),
        pytest.param("5 ^ 2 - 3", "22.0", id="045"),
        pytest.param("9 % 4 + 6", "7.0", id="046"),
        pytest.param("sin(pi / 4) * sqrt(2)", "1.0", id="047"),
        pytest.param("cos(0) + tan(pi / 4)", "2.0", id="048"),
        pytest.param("sinh(1) + cosh(1) - 1", "1.718281828459045", id="049"),
        pytest.param("exp(2) - ln(e^3) + 1", "5.38905609893065", id="050"),
        pytest.param("abs(-7) + trunc(3.78) - 2", "8.0", id="051"),
        pytest.param("round(4.56) + sgn(-10) + 2", "6.0", id="052"),
        pytest.param("log(1000) + log2(16) - log(100)", "5.0", id="053"),
        pytest.param("sqrt(25) + 3 * 2", "11.0", id="054"),
        pytest.param("e ^ 1 + pi - 4", "1.859874482048838", id="055"),
        pytest.param("10 += 5 - 3", "12.0", id="056"),
        pytest.param("20 -= 3 * 2", "14.0", id="057"),
        pytest.param("6 *= 2 + 1", "18.0", id="058"),
        pytest.param("18 /= 3 - 1", "9.0", id="059"),
        pytest.param("(-3) ^ 2 + 4", "13.0", id="060"),
        pytest.param("5 - (-2) + 7", "14.0", id="061"),
        pytest.param("10 / 2 + 3 - 1", "7.0", id="062"),
        pytest.param("-sqrt(49) + 5 * 2", "3.0", id="063"),
        pytest.param("cos(pi) + sin(-pi / 2) + 2", "0.0", id="064"),
        pytest.param("tanh(0.5) + sinh(1) - cosh(1)", "0.094237716088567", id="065"),
        pytest.param("log(0.1) + ln(1) + 4", "3.0", id="066"),
        pytest.param("sgn(-8) + trunc(-4.98) + 5", "0.0", id="067"),
        pytest.param("round(-3.5) + sqrt(16) - 2", "-2.0", id="068"),
        pytest.param("exp(1) + ln(e) - pi", "0.576689174869252", id="069"),
        pytest.param("cos(0) + tanh(1) * 2", "2.52318831191153", id="070"),
        pytest.param("5 + 3 * 2 - 4 / 2", "9.0", id="071"),
        pytest.param("(10 - 4) / 2 + 7 * 3", "24.0", id="072"),
        pytest.param("8 / 2 + 6 - 3 * 2", "4.0", id="073"),
        pytest.param("7 * 2 - 5 + 4 / 2", "11.0", id="074"),
        pytest.param("5 ^ 2 - 3 + sqrt(16)", "26.0", id="075"),
        pytest.param("9 % 4 + 6 - 2 * 3", "1.0", id="076"),
        pytest.param("sin(pi / 4) * sqrt(2) + cos(0)", "2.0", id="077"),
        pytest.param("cos(0) + tan(pi / 4) * 2 - 1", "2.0", id="078"),
        pytest.param(
            "sinh(1) + cosh(1) - 1 + tanh(0.5)",
            "2.180398985719055",
            id="079",
        ),
        pytest.param("exp(2) - ln(e^3) + 1 - log(10)", "4.38905609893065", id="080"),
        pytest.param("abs(-7) + trunc(3.78) - 2 + round(4.56)", "13.0", id="081"),
        pytest.param("round(4.56) + sgn(-10) + 2 - sqrt(9)", "3.0", id="082"),
        pytest.param("log(1000) + log2(16) - log(100) + 2", "7.0", id="083"),
        pytest.param("sqrt(25) + 3 * 2 - 4 / 2", "9.0", id="084"),
        pytest.param("e ^ 1 + pi - 4 + ln(e^2)", "3.859874482048838", id="085"),
        pytest.param("10 += 5 - 3 * 2 + 4", "13.0", id="086"),
        pytest.param("20 -= 3 * 2 + sqrt(9) - 1", "12.0", id="087"),
        pytest.param("6 *= 2 + 1 - 4 / 2", "6.0", id="088"),
        pytest.param("18 /= 3 - 1 + 5 * 2", "1.5", id="089"),
        pytest.param("(-3) ^ 2 + 4 - sqrt(16) + log2(32)", "14.0", id="090"),
        pytest.param("5 - (-2) + 7 - 3 * 2", "8.0", id="091"),
        pytest.param("10 / 2 + 3 - 1 * 5 + 4", "7.0", id="092"),
        pytest.param("-sqrt(49) + 5 * 2 - log(100)", "1.0", id="093"),
        pytest.param("cos(pi) + sin(-pi / 2) + 2 * 3 - 1", "3.0", id="094"),
        pytest.param(
            "tanh(0.5) + sinh(1) - cosh(1) + log(10)",
            "1.094237716088567",
            id="095",
        ),
        pytest.param("log(0.1) + ln(1) + 4 - sqrt(9) * 2", "-3.0", id="096"),
        pytest.param("sgn(-8) + trunc(-4.98) + 5 - round(2.6)", "-3.0", id="097"),
        pytest.param("round(-3.5) + sqrt(16) - 2 * 3 + 10", "4.0", id="098"),
        pytest.param("exp(1) + ln(e) - pi + sqrt(9)", "3.576689174869252", id="099"),
        pytest.param(
            "cos(0) + tanh(1) * 2 - sqrt(4) + log2(8)",
            "3.52318831191153",
            id="100",
        ),
        pytest.param("hypot(6, 8) + sqrt(25)", "15.0", id="101"),
        pytest.param(
            "log2(hypot(8, 15)) * round(3.5678, 2)",
            "14.59224234326371",
            id="102",
        ),
        pytest.param("hypot(7, 24) - tan(pi / 4) + 2", "26.0", id="103"),
        pytest.param("abs(-hypot(9, 40)) + trunc(5.99)", "46.0", id="104"),
        pytest.param("hypot(12, 16) / cos(0) + sinh(1)", "21.1752011936438", id="105"),
        pytest.param(
            "tau / 2 + sin(tau / 4) * sqrt(49)",
            "10.141592653589793",
            id="106",
        ),
        pytest.param(
            "hypot(10, tau) - log2(64) + cos(pi)",
            "4.810098120013967",
            id="107",
        ),
        pytest.param(
            "exp(1) * tau - round(3.1415, 2) + sinh(0)",
            "13.939468445347131",
            id="108",
        ),
        pytest.param(
            "tau ^ 2 / (hypot(3, 4) + log(100)) - 1",
            "4.639773943479633",
            id="109",
        ),
        pytest.param(
            "tau * cosh(1) - trunc(9.87) + abs(-5)",
            "5.695461572464488",
            id="110",
        ),
    ),
)
def test_dec_math_basic(
    expr: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:" + expr + "}"
    result = ts_interpreter.process(script).body
    assert result == out


# endregion

# region 111-141: 31 single operator/function expressions, tested with 'math' declaration


@pytest.mark.parametrize(
    ("expr", "out"),
    (
        pytest.param("12 + 7", "19.0", id="111_addition"),
        pytest.param("20 - 9", "11.0", id="112_subtraction"),
        pytest.param("4 * 6", "24.0", id="113_multiplication"),
        pytest.param("18 / 3", "6.0", id="114_division"),
        pytest.param("1 += 8", "9.0", id="115_i_addition"),
        pytest.param("1 -= 6", "-5.0", id="116_i_subtraction"),
        pytest.param("2 *= 5", "10.0", id="117_i_multiplication"),
        pytest.param("6 /= 2", "3.0", id="118_i_division"),
        pytest.param("2 ^ 4", "16.0", id="119_exponentiation"),
        pytest.param("15 % 7", "1.0", id="120_modulo"),
        pytest.param("sin(4)", "-0.756802495307928", id="121_sine"),
        pytest.param("cos(0.5)", "0.877582561890373", id="122_cosine"),
        pytest.param("tan(12)", "-0.635859928661581", id="123_tangens"),
        pytest.param("sinh(2)", "3.626860407847019", id="124_hyperbolic_sine"),
        pytest.param("cosh(2)", "3.762195691083631", id="125_hyperbolic_cosine"),
        pytest.param("tanh(2)", "0.964027580075817", id="126_hyperbolic_tangens"),
        pytest.param("exp(3)", "20.085536923187668", id="127_exponential_function"),
        pytest.param("abs(-12)", "12.0", id="128_absolute"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("trunc(9.99)", "9", id="129_truncation"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("round(2.51)", "3", id="130_no_arg_round"),
        #  no-arg round/trunc/sgn return int not float
        pytest.param("sgn(15)", "1", id="131_signum"),
        pytest.param("log(500)", "2.698970004336019", id="132_log_base_10"),
        pytest.param("ln(7.389)", "1.999992407806511", id="133_natural_log"),
        pytest.param("log2(32)", "5.0", id="134_log_base_2"),
        pytest.param("sqrt(36)", "6.0", id="135_sqrt"),
        pytest.param("e", "2.718281828459045", id="136_eulers_number"),
        pytest.param("pi", "3.141592653589793", id="137_pi"),
        pytest.param("tau", "6.283185307179586", id="138_tau"),
        pytest.param("+14", "14.0", id="139_unary_plus"),
        pytest.param("-9", "-9.0", id="140_unary_minus"),
        pytest.param("hypot(3, 4)", "5.0", id="141_hypotenuse"),
    ),
)
def test_dec_math_single_operation(
    expr: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:" + expr + "}"
    result = ts_interpreter.process(script).body
    assert result == out


# endregion

# region 142-147: 6 random multi-arg round expressions, tested with 'math' declaration


@pytest.mark.parametrize(
    ("expr", "out"),
    (
        pytest.param("round(3.141592, 1)", "3.1", id="142"),
        pytest.param("round(9.87654, 3)", "9.877", id="143"),
        pytest.param("round(27.4392, 2)", "27.44", id="144"),
        pytest.param("round(0.987654, 4)", "0.9877", id="145"),
        pytest.param("round(123.456789, 5)", "123.45679", id="146"),
        pytest.param("round(12345, -2)", "12300.0", id="147"),
    ),
)
def test_dec_math_random_multi_arg_round(
    expr: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:" + expr + "}"
    result = ts_interpreter.process(script).body
    assert result == out


# endregion

# region 148-151: 4 random literal π/τ expressions, tested with 'math' declaration


@pytest.mark.parametrize(
    ("expr", "out"),
    (
        pytest.param("sin(π / 2) + sqrt(16)", "5.0", id="148"),
        pytest.param("cos(π) * 2 + 3", "1.0", id="149"),
        pytest.param("tan(τ / 3) + log2(8)", "1.267949192431122", id="150"),
        pytest.param("hypot(5, τ) - round(3.14, 1)", "4.929845428422482", id="151"),
    ),
)
def test_dec_math_random_literal_constants(
    expr: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{math:" + expr + "}"
    result = ts_interpreter.process(script).body
    assert result == out


# endregion
