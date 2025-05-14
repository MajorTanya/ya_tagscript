from unittest.mock import MagicMock, patch

import pytest
from discord.ext.commands import CooldownMapping

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.CooldownBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


@pytest.fixture
def mock_cm():
    with patch(
        "ya_tagscript.blocks.discord.cooldown_block.CooldownMapping",
        spec=CooldownMapping,
        wraps=CooldownMapping,
    ) as mocked_cm:
        bucket_mock = MagicMock()
        # This was a pain to properly mock but this is what is needed
        mocked_cm.from_cooldown.return_value = bucket_mock
        bucket_mock.get_bucket.return_value = None
        yield mocked_cm


def test_accepted_names():
    block = blocks.CooldownBlock()
    assert block._accepted_names == {"cooldown"}


def test_process_method_rejects_missing_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = ""

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_parameter():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "     "

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = None

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = ""

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = "I have to be valid to pass the first check"
    mock_ctx.node.payload = "     "

    block = blocks.CooldownBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_cooldown_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=1))}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    response = ts_interpreter.process(script, data)
    assert response.body != ""
    assert (
        response.body
        == "The bucket for 1 has reached its cooldown. Retry in 10.0 seconds."
    )


def test_dec_cooldown_empty_parameter_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown():{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=2))}
    result = ts_interpreter.process(script, data).body
    assert result == "{cooldown():2}"


def test_dec_cooldown_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|10):}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=3))}
    result = ts_interpreter.process(script, data).body
    assert result == script


def test_dec_cooldown_exceeding_uses_get_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=4))}
    result = ts_interpreter.process(script, data).body
    assert result == ""
    result = ts_interpreter.process(script, data).body
    assert result == "The bucket for 4 has reached its cooldown. Retry in 10.0 seconds."


def test_dec_cooldown_custom_message_used_when_exceeding_uses_get_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|10):{author(id)}|Cooldown hit! Try again in {retry_after} seconds.}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=5))}
    result = ts_interpreter.process(script, data).body
    assert result == ""
    result = ts_interpreter.process(script, data).body
    assert result == "Cooldown hit! Try again in 10.0 seconds."


def test_dec_cooldown_uses_extra_cooldown_key_kwarg(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=6))}
    extras_1 = {"cooldown_key": "my key"}
    result = ts_interpreter.process(script, data, extras_1).body
    assert result == ""
    result = ts_interpreter.process(script, data, extras_1).body
    assert result == "The bucket for 6 has reached its cooldown. Retry in 10.0 seconds."
    extras_2 = {"cooldown_key": "other key"}
    result = ts_interpreter.process(script, data, extra_kwargs=extras_2).body
    assert result == ""
    result = ts_interpreter.process(script, data, extras_1).body
    # checking for an exact cooldown is futile, just make sure the tag doesn't
    # pass using the previous key
    assert result != ""


def test_dec_cooldown_changing_rate_per_is_respected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(5|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=7))}
    result = ts_interpreter.process(script, data).body
    assert result == ""
    result = ts_interpreter.process(script, data).body
    assert result == ""
    new_script = "{cooldown(1|10):{author(id)}}"
    result = ts_interpreter.process(new_script, data).body
    assert result == ""
    result = ts_interpreter.process(new_script, data).body
    assert result == "The bucket for 7 has reached its cooldown. Retry in 10.0 seconds."


def test_dec_cooldown_changing_rate_per_with_custom_key_is_respected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(5|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=8))}
    extras = {"cooldown_key": "my key"}
    result = ts_interpreter.process(script, data, extras).body
    assert result == ""
    result = ts_interpreter.process(script, data, extras).body
    assert result == ""
    new_script = "{cooldown(1|10):{author(id)}}"
    result = ts_interpreter.process(new_script, data, extras).body
    assert result == ""
    result = ts_interpreter.process(new_script, data, extras).body
    assert result == "The bucket for 8 has reached its cooldown. Retry in 10.0 seconds."


def test_dec_cooldown_non_float_rate_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(x|10):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=9))}
    result = ts_interpreter.process(script, data).body
    assert result == "{cooldown(x|10):9}"


def test_dec_cooldown_non_float_per_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|y):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=10))}
    result = ts_interpreter.process(script, data).body
    assert result == "{cooldown(1|y):10}"


def test_dec_cooldown_non_float_rate_and_per_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(x|y):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=11))}
    result = ts_interpreter.process(script, data).body
    assert result == "{cooldown(x|y):11}"


def test_dec_cooldown_incomplete_rate_per_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1):{author(id)}}"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=12))}
    result = ts_interpreter.process(script, data).body
    assert result == "{cooldown(1):12}"


def test_dec_cooldown_if_bucket_is_none_do_not_limit(
    ts_interpreter: TagScriptInterpreter,
    mock_cm: MagicMock,
):
    # the mock_cm is not directly accessed but is patches the CooldownMapping class's
    # from_cooldown class method which is what this test is handling
    # ---
    # this is a somewhat useless test since buckets should never be None but since
    # d.py typed get_bucket as Optional and pyright goes by that, make sure the
    # fallback on "let's assume this is allowed" works correctly for this
    # eventuality
    script = "{cooldown(1|10):{author(id)}}Hello"
    data = {"author": adapters.AttributeAdapter(MagicMock(id=451))}
    result = ts_interpreter.process(script, data).body
    assert result == "Hello"
    result = ts_interpreter.process(script, data).body
    assert result == "Hello"


def test_dec_cooldown_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown({my_var}):key}"
    data = {"my_var": adapters.StringAdapter("1|10")}
    result = ts_interpreter.process(script, data).body
    assert result == ""
    result = ts_interpreter.process(script, data).body
    assert (
        result == "The bucket for key has reached its cooldown. Retry in 10.0 seconds."
    )


def test_dec_cooldown_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{cooldown(1|5):{my_var}}"
    data = {"my_var": adapters.StringAdapter("key-two")}
    result = ts_interpreter.process(script, data).body
    assert result == ""
    result = ts_interpreter.process(script, data).body
    assert (
        result
        == "The bucket for key-two has reached its cooldown. Retry in 5.0 seconds."
    )
