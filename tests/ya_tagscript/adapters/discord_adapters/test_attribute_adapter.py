from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_attr_count_is_correct():
    obj = MagicMock()
    a = adapters.AttributeAdapter(obj)
    # id, created_at, timestamp, name = 4 attrs total
    assert len(a._attributes) == 4


def test_method_count_is_correct():
    obj = MagicMock()
    a = adapters.AttributeAdapter(obj)
    # no methods = 0 methods total
    assert len(a._methods) == 0


def test_no_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj}"
    obj = MagicMock()
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_empty_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj()}"
    obj = MagicMock()
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_id_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(id)}"
    obj = MagicMock(id=123)
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "123"


def test_name_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(name)}"
    obj = MagicMock()
    obj.name = "obj name"
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj name"


def test_created_at_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(created_at)}"
    dt = datetime(2025, 1, 1, 0, 0, 1, tzinfo=UTC)
    obj = MagicMock(created_at=dt)
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 00:00:01+00:00"


def test_timestamp_attr_based_on_created_at_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(timestamp)}"
    dt = datetime(2025, 1, 1, 0, 0, 1, tzinfo=UTC)
    obj = MagicMock(created_at=dt)
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_invalid_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_obj(fancy)}"
    obj = MagicMock()
    obj.fancy.side_effect = AttributeError
    data = {"my_obj": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script
