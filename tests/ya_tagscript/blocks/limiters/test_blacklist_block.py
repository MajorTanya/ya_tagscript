from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.BlacklistBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.BlacklistBlock()
    assert block._accepted_names == {"blacklist"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.BlacklistBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.BlacklistBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.BlacklistBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_blacklist_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(Muted)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["Muted"],
        "response": None,
    }


def test_dec_blacklist_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(#support):This tag is not allowed in #support.}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["#support"],
        "response": "This tag is not allowed in #support.",
    }


def test_dec_blacklist_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(Tag Blacklist, 668713062186090506):You are blacklisted from using tags.}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["Tag Blacklist", "668713062186090506"],
        "response": "You are blacklisted from using tags.",
    }


def test_dec_blacklist_only_first_blacklist_block_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(123):Blocked!}{blacklist(987):Blocked too!}"
    response = ts_interpreter.process(script)
    assert response.body == "{blacklist(987):Blocked too!}"
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["123"],
        "response": "Blocked!",
    }


def test_dec_blacklist_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist({my_var})}"
    data = {
        "my_var": adapters.StringAdapter("456"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["456"],
        "response": None,
    }


def test_dec_blacklist_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(this role,other role):{my_var}}"
    data = {
        "my_var": adapters.StringAdapter("this is a block message"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["this role", "other role"],
        "response": "this is a block message",
    }


def test_dec_blacklist_following_blocks_are_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{blacklist(123):You got blocked!}{myvar}"
    data = {
        "myvar": adapters.StringAdapter("hello world"),
    }
    response = ts_interpreter.process(script, data)
    blacklisted = response.actions.get("blacklist")
    assert blacklisted is not None
    assert blacklisted == {
        "items": ["123"],
        "response": "You got blocked!",
    }
    assert response.body == "hello world"
