from unittest.mock import MagicMock

from ya_tagscript import interpreter

# noinspection PyProtectedMember
from ya_tagscript.util.conditionals import (
    _execute_operator,
    _find_zero_depth_operator,
    parse_condition,
)


def test_simple_equals_with_text():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "this==this"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_not_equals_with_text():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "this!=that"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_equals():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1==1"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_not_equals():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1!=2"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_less_than_or_equal():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1<=2"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_greater_than_or_equal():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "2>=1"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_less_than():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1<2"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_greater_than():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "2>1"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_equals_with_text_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "this==that"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_not_equals_with_text_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "this!=this"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_equals_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1==2"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_not_equals_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1!=1"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_less_than_or_equal_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1<=0"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_greater_than_or_equal_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "0>=1"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_less_than_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "2<2"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_greater_than_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "2>2"
    out = parse_condition(mock_ctx, script)
    assert not out


def test_simple_unsupported_operator():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "1??2"
    out = parse_condition(mock_ctx, script)
    assert out is None


def test_simple_constant_true():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "true"
    out = parse_condition(mock_ctx, script)
    assert out


def test_simple_constant_false():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x

    script = "false"
    out = parse_condition(mock_ctx, script)
    assert not out


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
