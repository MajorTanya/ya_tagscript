from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.ShortcutRedirectBlock("args"),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    # returns None intentionally
    block = blocks.ShortcutRedirectBlock("test")
    assert block._accepted_names is None


def test_will_accept_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.ShortcutRedirectBlock("args")
    assert not block.will_accept(mock_ctx)


def test_will_accept_rejects_non_numeric_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "123Fail"

    block = blocks.ShortcutRedirectBlock("args")
    assert not block.will_accept(mock_ctx)


def test_redirect_resolves_correctly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{1}"
    data = {"args": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "hello"


def test_redirect_gets_resolved_even_without_target_existing(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{1}"
    data = {"notargs": adapters.StringAdapter("hello world")}
    result = ts_interpreter.process(script, data).body
    assert result == "{args(1)}"
