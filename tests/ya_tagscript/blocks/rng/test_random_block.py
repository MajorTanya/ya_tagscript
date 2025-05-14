from unittest.mock import MagicMock

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.RandomBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.RandomBlock()
    assert block._accepted_names == {"random", "rand", "#"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.RandomBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = ""

    block = blocks.RandomBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = "     "

    block = blocks.RandomBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_random_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:Carl,Harold,Josh} attempts to pick the lock!"
    result = ts_interpreter.process(script).body
    assert result in (
        "Carl attempts to pick the lock!",
        "Harold attempts to pick the lock!",
        "Josh attempts to pick the lock!",
    )


def test_dec_random_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:5|Cool,3|Lame}"
    result = ts_interpreter.process(script).body
    assert result in ("Cool", "Lame")


def test_dec_random_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:first,10|second,third,4|fourth}"
    result = ts_interpreter.process(script).body
    assert result in ("first", "second", "third", "fourth")


def test_dec_random_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{assign(items):hello~hi~good morning}{assign(seed):123}{random({seed}):{items}}"
    result = ts_interpreter.process(script).body
    assert result == "good morning"


def test_dec_random_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_random_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_random_no_seed_no_weight(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:Apple~Banana~Cherry}"
    result = ts_interpreter.process(script).body
    assert result in ("Apple", "Banana", "Cherry")


def test_dec_random_no_seed_partial_weights(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:Apple~20|Banana~9|Cherry}"
    result = ts_interpreter.process(script).body
    assert result in ("Apple", "Banana", "Cherry")


def test_dec_random_no_seed_full_weights(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random:1|Apple~2|Banana~9|Cherry}"
    result = ts_interpreter.process(script).body
    assert result in ("Apple", "Banana", "Cherry")


def test_dec_random_seed_no_weight(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random(seed):Apple~Banana~Cherry}"
    result = ts_interpreter.process(script).body
    assert result == "Apple"


def test_dec_random_empty_seed_no_weight(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random():Apple~Banana~Cherry}"
    result = ts_interpreter.process(script).body
    assert result == "Cherry"


def test_dec_random_seed_partial_weights(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random(other seed):Apple~20|Banana~9|Cherry}"
    result = ts_interpreter.process(script).body
    assert result == "Banana"


def test_dec_random_seed_full_weights(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random(third seed):1|Apple~2|Banana~9|Cherry}"
    result = ts_interpreter.process(script).body
    assert result == "Cherry"


def test_dec_random_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random({my_var}):Apple~Banana~Cherry}"
    data = {"my_var": adapters.IntAdapter(123)}
    script2 = "{random(123):Apple~Banana~Cherry}"
    result = ts_interpreter.process(script, data).body
    result2 = ts_interpreter.process(script2).body
    assert result2 == result


def test_dec_random_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random(9876543210):{my_var}}"
    data = {"my_var": adapters.StringAdapter("Apple~Banana~Cherry")}
    result = ts_interpreter.process(script, data).body
    assert result == "Apple"


def test_dec_random_payload_items_are_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{random(234):{my_var}}"
    data = {
        "my_var": adapters.StringAdapter("{one}{=(xyz):test}~{two}"),
        "one": adapters.StringAdapter("first outcome"),
        "two": adapters.StringAdapter("second outcome"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == "second outcome"
    # proof that the first section did not get interpreted
    assert response.variables.get("xyz") is None
