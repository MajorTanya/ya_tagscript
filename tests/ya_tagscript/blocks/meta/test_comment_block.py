from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, blocks, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.CommentBlock(),
    ]
    return TagScriptInterpreter(b)


@pytest.fixture
def ts_interpreter_with_cmd_block():
    b = [
        blocks.CommentBlock(),
        blocks.CommandBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.CommentBlock()
    assert block._accepted_names == {"/", "//", "comment"}


def test_process_method_does_not_touch_ctx():
    block = blocks.CommentBlock()
    mock_ctx = MagicMock(spec=interpreter.Context)
    result = block.process(mock_ctx)
    mock_ctx.assert_not_called()
    assert result == ""


def test_dec_comment_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{comment:My Comment!}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_comment_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{comment(Something):My Comment!}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_comment_docs_example_three(
    ts_interpreter_with_cmd_block: TagScriptInterpreter,
):
    script = "{comment:{cmd:echo hello world}}{cmd:ping}"
    response = ts_interpreter_with_cmd_block.process(script)
    assert response.actions.get("commands") == ["ping"]
    assert response.body == ""
