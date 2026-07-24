# pyright: reportPrivateUsage=false
import pytest

from ya_tagscript import TagScriptInterpreter, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.SilenceBlock(),
    ]
    return TagScriptInterpreter(b)


def test_valid_names():
    block = blocks.SilenceBlock()
    assert block._VALID_NAMES == {"silence", "silent"}


def test_dec_silence_sets_silence_action(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{silence}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    assert response.actions.get(blocks.SilenceBlock.ACTIONS_KEY)
