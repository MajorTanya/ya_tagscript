import re

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(blocks=b)


def test_int_is_stored(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_int}"
    data = {"my_int": adapters.IntAdapter(42)}
    response = ts_interpreter.process(script, data)
    assert response.body == "42"


def test_float_is_truncated(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_float}"
    data = {"my_float": adapters.IntAdapter(42.5)}  # type: ignore
    response = ts_interpreter.process(script, data)
    assert response.body == "42"


def test_failed_int_conversion_raises():
    with pytest.raises(
        ValueError,
        match=re.escape(
            "invalid literal for int() with base 10: 'really broken input'",
        ),
    ):
        adapters.IntAdapter("really broken input")  # type: ignore
