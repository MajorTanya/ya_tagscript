from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.FiftyFiftyBlock(),
        blocks.IfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.FiftyFiftyBlock()
    assert block._accepted_names == {"5050", "50", "?"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.FiftyFiftyBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_5050_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "I pick {if({5050:.}!=):heads|tails}"
    result = ts_interpreter.process(script).body
    assert result in ["I pick heads", "I pick tails"]


def test_dec_5050_empty_payload_results_in_identical_outcomes(
    ts_interpreter: TagScriptInterpreter,
):
    script = "Out={5050:}"
    result = ts_interpreter.process(script).body
    # These tests are a bit weird, but since 5050 either returns the payload or an
    # empty string, and we provide an empty string here, it'll always result in an
    # empty string
    # Obviously, because there is randomness involved, this test may not fail the
    # first time the block's functionality is broken, but it would eventually
    # Think of it like a very inattentive canary in a mine
    # Also, this shows the block was processed and replaced with its output
    assert result == "Out="


def test_dec_5050_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{5050}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_5050_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{5050:{my_var}}"
    data = {"my_var": adapters.StringAdapter("outcome")}
    result = ts_interpreter.process(script, data).body
    assert result in {"", "outcome"}
