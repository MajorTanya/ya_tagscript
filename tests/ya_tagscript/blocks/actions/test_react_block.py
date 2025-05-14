from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.ReactBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.ReactBlock()
    assert block._accepted_names == {"react", "reactu"}


def test_process_method_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = ""

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "     "

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_invalid_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.interpret_segment = lambda x: x
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "something else"
    mock_ctx.node.payload = "something else"

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "valid to pass"
    mock_ctx.node.payload = None

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "valid to pass"
    mock_ctx.node.payload = ""

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "valid to pass"
    mock_ctx.node.payload = "     "

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_react_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["💩"]}


def test_dec_reactu_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["👍"]}


def test_dec_react_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩 :)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["💩", ":)"]}


def test_dec_reactu_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍 ⏰}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["👍", "⏰"]}


def test_dec_react_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩 :) :D}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["💩", ":)", ":D"]}


def test_dec_reactu_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍 ⏰ 🦚}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["👍", "⏰", "🦚"]}


def test_dec_react_reactu_can_be_used_together(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:☕ 🤔}{reactu:🦚 🦫 💪}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {
        "input": ["🦚", "🦫", "💪"],
        "output": ["☕", "🤔"],
    }


def test_dec_react_repeated_use_overwrites_previous_emoji(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:🦚}{react:🦫}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["🦫"]}


def test_dec_reactu_repeated_use_overwrites_previous_emoji(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:🦚}{reactu:🦫}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["🦫"]}


def test_dec_react_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:}"
    response = ts_interpreter.process(script)
    assert response.body == script
    assert response.actions.get("reactions") is None


def test_dec_reactu_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:}"
    response = ts_interpreter.process(script)
    assert response.body == script
    assert response.actions.get("reactions") is None


def test_dec_react_limit_is_enforced(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:✅ ☕ 🤔 👍 😅 💩}"
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    assert response.actions.get("reactions") is None


def test_dec_reactu_limit_is_enforced(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:✅ ☕ 🤔 👍 😅 💩}"
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    assert response.actions.get("reactions") is None


def test_dec_react_reactu_limit_is_enforced_per_variant_not_globally(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:✅ ☕ 🤔 👍 😅 💩}{reactu:☕ 🤔 👍 😅}"
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["☕", "🤔", "👍", "😅"]}


def test_dec_reactu_react_limit_is_enforced_per_variant_not_globally(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:☕ 🤔 👍 😅}{reactu:✅ ☕ 🤔 👍 😅 💩}"
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["☕", "🤔", "👍", "😅"]}


def test_dec_react_nested_payload_is_parsed_and_split_correctly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:{=(a):A}{=(b):{a} B}{b}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": ["A", "B"]}


def test_dec_reactu_nested_payload_is_parsed_and_split_correctly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:{=(a):A}{=(b):{a} B}{b}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": ["A", "B"]}


def test_dec_react_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:{myvar}}"
    data = {"myvar": adapters.StringAdapter(":waving:")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"output": [":waving:"]}


def test_dec_reactu_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:{myvar}}"
    data = {"myvar": adapters.StringAdapter(":waving:")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    reactions = response.actions.get("reactions")
    assert reactions is not None
    assert reactions == {"input": [":waving:"]}
