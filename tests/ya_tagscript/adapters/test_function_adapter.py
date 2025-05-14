from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, exceptions


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_fn_is_called(
    ts_interpreter: TagScriptInterpreter,
):
    my_fn = MagicMock(return_value="hello world")
    script = "{fn}"
    data = {"fn": adapters.FunctionAdapter(my_fn)}
    result = ts_interpreter.process(script, data).body
    my_fn.assert_called_once()
    assert result == "hello world"


def test_repeated_fn_is_called_exactly_as_many_times(
    ts_interpreter: TagScriptInterpreter,
):
    my_fn = MagicMock(return_value="hello world")
    script = "{fn}! {fn}!"
    data = {"fn": adapters.FunctionAdapter(my_fn)}
    result = ts_interpreter.process(script, data).body
    my_fn.assert_called()
    assert my_fn.call_count == 2
    assert result == "hello world! hello world!"


def test_fn_raises(
    ts_interpreter: TagScriptInterpreter,
):
    my_fn = MagicMock(side_effect=Exception("RAISED"))
    script = "{fn}"
    data = {"fn": adapters.FunctionAdapter(my_fn)}
    with pytest.raises(exceptions.ProcessError, match="RAISED"):
        ts_interpreter.process(script, data)
    my_fn.assert_called_once()
