import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks
from ya_tagscript.util import escape_content


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_escapes_should_apply(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{if({msg}==):provide a message|{msg}}"
    msg = escape_content("message provided :")
    assert msg is not None
    assert isinstance(msg, str)
    data = {"msg": adapters.StringAdapter(msg)}
    result = ts_interpreter.process(script, data).body
    assert result == "message provided \\:"


def test_escape_content_returns_none_if_input_is_none():
    assert escape_content(None) is None
