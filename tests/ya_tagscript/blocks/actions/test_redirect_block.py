from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.RedirectBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.RedirectBlock()
    assert block._accepted_names == {"redirect"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.RedirectBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.RedirectBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "    "

    block = blocks.RedirectBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_redirect_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect(dm)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("target") == "dm"


def test_dec_redirect_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect(reply)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("target") == "reply"


def test_dec_redirect_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect(#general)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("target") == "#general"


def test_dec_redirect_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect(1195734229506601003)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("target") == "1195734229506601003"


def test_dec_redirect_repeated_use_overwrites_previous_target(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect(dm)}{redirect(reply)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get("target") == "reply"


def test_dec_redirect_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{redirect({myvar})}"
    data = {"myvar": adapters.StringAdapter("dm")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    assert response.actions.get("target") == "dm"
