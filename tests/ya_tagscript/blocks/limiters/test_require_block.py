from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.RequireBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.RequireBlock()
    assert block._accepted_names == {"require", "whitelist"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.RequireBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.RequireBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.RequireBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_require_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(Moderator)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["Moderator"],
        "response": None,
    }


def test_dec_require_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(#general, #bot-cmds):This tag can only be run in #general and #bot-cmds.}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["#general", "#bot-cmds"],
        "response": "This tag can only be run in #general and #bot-cmds.",
    }


def test_dec_require_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(757425366209134764, 668713062186090506, 737961895356792882):You aren't allowed to use this tag.}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": [
            "757425366209134764",
            "668713062186090506",
            "737961895356792882",
        ],
        "response": "You aren't allowed to use this tag.",
    }


def test_dec_require_only_first_require_block_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(123):Blocked!}{require(987):Blocked too!}"
    response = ts_interpreter.process(script)
    assert response.body == "{require(987):Blocked too!}"
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["123"],
        "response": "Blocked!",
    }


def test_dec_require_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require({my_var})}"
    data = {"my_var": adapters.StringAdapter("456")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["456"],
        "response": None,
    }


def test_dec_require_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(this role,other role):{my_var}}"
    data = {"my_var": adapters.StringAdapter("this is a block message")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["this role", "other role"],
        "response": "this is a block message",
    }


def test_dec_require_following_blocks_are_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{require(123):You got blocked!}{myvar}"
    data = {
        "myvar": adapters.StringAdapter("hello world"),
    }
    response = ts_interpreter.process(script, data)
    required = response.actions.get("requires")
    assert required is not None
    assert required == {
        "items": ["123"],
        "response": "You got blocked!",
    }
    assert response.body == "hello world"
