# pyright: reportPrivateUsage=false
from unittest.mock import Mock

import pytest

from ya_tagscript import interpreter

# noinspection PyProtectedMember
from ya_tagscript.util.conditionals import (
    _execute_operator,
    _find_zero_depth_operator,
    parse_condition,
)


@pytest.mark.parametrize(
    ("script", "expected"),
    (
        pytest.param("this==this", True, id="eq-text"),
        pytest.param("this!=that", True, id="neq-text"),
        pytest.param("1==1", True, id="eq-ints"),
        pytest.param("1!=2", True, id="neq-ints"),
        pytest.param("1<=2", True, id="lte-ints"),
        pytest.param("2>=1", True, id="gte-ints"),
        pytest.param("1<2", True, id="lt-ints"),
        pytest.param("2>1", True, id="gt-ints"),
        pytest.param("this==that", False, id="eq-text-false"),
        pytest.param("this!=this", False, id="neq-text-false"),
        pytest.param("1==2", False, id="eq-ints-false"),
        pytest.param("1!=1", False, id="neq-ints-false"),
        pytest.param("1<=0", False, id="lte-ints-false"),
        pytest.param("0>=1", False, id="gtw-ints-false"),
        pytest.param("2<2", False, id="lt-ints-false"),
        pytest.param("2>2", False, id="gt-ints-false"),
        pytest.param("1??2", None, id="unsupported-operator"),
        pytest.param("true", True, id="literal-true"),
        pytest.param("false", False, id="literal-false"),
    ),
)
def test_simple_conditions(
    script: str,
    expected: bool,
):
    mock_ctx = Mock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    out = parse_condition(mock_ctx, script)
    assert out == expected


def test_simple_unsupported_operator():
    mock_ctx = Mock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1??2"
    out = parse_condition(mock_ctx, script)
    assert out is None


def test_executing_invalid_operator_returns_none():
    out = _execute_operator("hello", "??", "world")
    assert out is None


def test_simple_operator_search():
    script = "1==2"
    out = _find_zero_depth_operator(script)
    assert out is not None
    assert out.start_idx == 1
    assert out.end_idx == 3
    assert out.operator == "=="


def test_nested_operator_search():
    script = "{1<=2!=3}!=4"
    out = _find_zero_depth_operator(script)
    assert out is not None
    assert out.start_idx == 9
    assert out.end_idx == 11
    assert out.operator == "!="


def test_doubly_nested_operator_search():
    script = "{1<=2!=3}{4ssklkl === 3.2}<{{kjsldkj}<=dddd}"
    out = _find_zero_depth_operator(script)
    assert out is not None
    assert out.start_idx == 26
    assert out.end_idx == 27
    assert out.operator == "<"
