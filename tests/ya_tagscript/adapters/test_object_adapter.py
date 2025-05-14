from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


class Dummy:  # pragma: no cover
    def dummy_method(self):
        pass


@pytest.fixture
def dummy():
    return Dummy()


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_no_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj}"
    obj = MagicMock()
    obj.__str__.return_value = "<obj dunder str>"  # type: ignore
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "<obj dunder str>"


def test_param_attr_is_returned(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(txt)}"
    obj = MagicMock()
    obj.txt = "hello world"
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "hello world"


def test_float_attr_is_truncated_to_int(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(other)}"
    obj = MagicMock()
    obj.other = 4.5
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "4"


def test_method_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
    dummy: Dummy,
):
    script = "{my_obj(call_this)}"
    obj = MagicMock()
    # using some method to mock being a method and pass ismethod check
    obj.call_this = MagicMock(spec=dummy.dummy_method)
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    obj.call_this.assert_not_called()
    assert result == script


def test_non_existent_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(totally_real)}"
    # just need something that doesn't have a 'totally_real' attr for the spec
    obj = MagicMock(spec=enumerate)
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script


def test_private_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(_private_int)}"
    obj = MagicMock()
    obj._private_int = 4
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script


def test_nested_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(nested.x)}"
    obj = MagicMock()
    obj.nested = MagicMock(x=1)
    data = {"my_obj": adapters.ObjectAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script
