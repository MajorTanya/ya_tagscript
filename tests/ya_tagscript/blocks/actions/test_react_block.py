# pyright: reportPrivateUsage=false
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


def test_valid_names():
    block = blocks.ReactBlock()
    assert block._VALID_NAMES == {"react", "reactu"}


@pytest.mark.parametrize(
    "declaration",
    (
        pytest.param(None, id="missing"),
        pytest.param("", id="empty"),
        pytest.param("    ", id="whitespace"),
    ),
)
def test_process_method_rejects_invalid_declarations(
    declaration: str | None,
):

    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = declaration

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


@pytest.mark.parametrize(
    "payload",
    (
        pytest.param(None, id="missing"),
        pytest.param("", id="empty"),
        pytest.param("    ", id="whitespace"),
    ),
)
def test_process_method_rejects_invalid_payloads(
    payload: str | None,
):
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "valid to pass"
    mock_ctx.node.payload = payload

    block = blocks.ReactBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_react_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"output": ["💩"]}


def test_dec_reactu_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"input": ["👍"]}


def test_dec_react_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩 :)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"output": ["💩", ":)"]}


def test_dec_reactu_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍 ⏰}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"input": ["👍", "⏰"]}


def test_dec_react_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:💩 :) :D}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"output": ["💩", ":)", ":D"]}


def test_dec_reactu_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{reactu:👍 ⏰ 🦚}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {"input": ["👍", "⏰", "🦚"]}


def test_dec_react_reactu_can_be_used_together(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{react:☕ 🤔}{reactu:🦚 🦫 💪}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {
        "input": ["🦚", "🦫", "💪"],
        "output": ["☕", "🤔"],
    }


@pytest.mark.parametrize(
    ("variant", "out_key"),
    (
        ("react", "output"),
        ("reactu", "input"),
    ),
)
def test_both_repeated_use_overwrites_previous_emoji(
    variant: str,
    out_key: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{{variant}:🦚}}{{{variant}:🦫}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {out_key: ["🦫"]}


@pytest.mark.parametrize(
    "variant",
    ("react", "reactu"),
)
def test_both_empty_payload_is_rejected(
    variant: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{{variant}:}}"
    response = ts_interpreter.process(script)
    assert response.body == script
    assert response.actions.get(blocks.ReactBlock.ACTIONS_KEY) is None


@pytest.mark.parametrize(
    "variant",
    ("react", "reactu"),
)
def test_both_limit_is_enforced(
    variant: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{{variant}:✅ ☕ 🤔 👍 😅 💩}}"
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    assert response.actions.get(blocks.ReactBlock.ACTIONS_KEY) is None


@pytest.mark.parametrize(
    ("limited_variant", "pass_variant", "out_key"),
    (
        ("react", "reactu", "input"),
        ("reactu", "react", "output"),
    ),
)
def test_both_limit_is_enforced_per_variant_not_globally(
    limited_variant: str,
    pass_variant: str,
    out_key: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{"  # line break comment
        + limited_variant
        + ":✅ ☕ 🤔 👍 😅 💩}{"
        + pass_variant
        + ":☕ 🤔 👍 😅}"
    )
    response = ts_interpreter.process(script)
    assert response.body == "`Reaction Limit Reached (5)`"
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {out_key: ["☕", "🤔", "👍", "😅"]}


@pytest.mark.parametrize(
    ("variant", "out_key"),
    (
        ("react", "output"),
        ("reactu", "input"),
    ),
)
def test_both_duplicate_spaces_between_emoji_are_ignored(
    variant: str,
    out_key: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{{variant}:         ✅   ☕     🦫    ♥️                  ⏰    }}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {out_key: ["✅", "☕", "🦫", "♥️", "⏰"]}


@pytest.mark.parametrize(
    ("variant", "out_key"),
    (
        ("react", "output"),
        ("reactu", "input"),
    ),
)
def test_both_nested_payload_is_parsed_and_split_correctly(
    variant: str,
    out_key: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{" + variant + ":{=(a):A}{=(b):{a} B}{b}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {out_key: ["A", "B"]}


@pytest.mark.parametrize(
    ("variant", "out_key"),
    (
        ("react", "output"),
        ("reactu", "input"),
    ),
)
def test_both_payload_is_interpreted(
    variant: str,
    out_key: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{" + variant + ":{myvar}}"
    data = {"myvar": adapters.StringAdapter(":waving:")}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    reactions = response.actions.get(blocks.ReactBlock.ACTIONS_KEY)
    assert reactions is not None
    assert reactions == {out_key: [":waving:"]}
