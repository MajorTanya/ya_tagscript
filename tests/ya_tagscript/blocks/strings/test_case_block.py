from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.CaseBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.CaseBlock()
    assert block._accepted_names == {"upper", "lower"}


def test_process_method_rejects_missing_declaration():
    # ludicrously impossible but necessary precaution since the block behaviour
    # depends on the declaration used
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.CaseBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_illegal_declaration():
    # would never happen because of will_accept but technically defined behaviour
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "something else"
    mock_ctx.node.payload = "yet something else"  # needs to be valid to go further

    block = blocks.CaseBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_returns_empty_string_on_missing_payload():
    # ludicrously impossible but necessary precaution since the block behaviour
    # depends on the declaration used
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "upper"  # valid to pass the first check
    mock_ctx.node.payload = None

    block = blocks.CaseBlock()
    returned = block.process(mock_ctx)
    assert returned == ""


def test_process_method_returns_empty_string_on_empty_payload():
    # ludicrously impossible but necessary precaution since the block behaviour
    # depends on the declaration used
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "upper"  # valid to pass the first check
    mock_ctx.node.payload = ""

    block = blocks.CaseBlock()
    returned = block.process(mock_ctx)
    assert returned == ""


def test_dec_upper_empty_payload(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper:}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_lower_empty_payload(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{lower:}"
    result = ts_interpreter.process(script).body
    assert result == ""


def test_dec_upper(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper:this should be uppercased}"
    result = ts_interpreter.process(script).body
    assert result == "THIS SHOULD BE UPPERCASED"


def test_dec_lower(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{lower:THIS SHOULD BE LOWERCASED}"
    result = ts_interpreter.process(script).body
    assert result == "this should be lowercased"


def test_dec_upper_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper:{my_var}}"
    data = {"my_var": adapters.StringAdapter("this is sparta!")}
    result = ts_interpreter.process(script, data).body
    assert result == "THIS IS SPARTA!"


def test_dec_upper_parameter_is_ignored_and_not_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper({=(my_var):test}):uppercased}"
    response = ts_interpreter.process(script)
    assert response.body == "UPPERCASED"
    # assignment block doesn't get called upon so my_var is not actually set
    assert response.variables == {}
