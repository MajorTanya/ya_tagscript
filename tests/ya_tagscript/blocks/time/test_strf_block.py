from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrfBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


@pytest.fixture
def mock_dt():
    with patch(
        "ya_tagscript.blocks.time.strf_block.datetime",
        spec=datetime,
        wraps=datetime,
    ) as mocked_dt:
        mocked_dt.now.return_value = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
        yield mocked_dt


def test_accepted_names():
    block = blocks.StrfBlock()
    assert block._accepted_names == {"strf", "unix"}


def test_process_method_rejects_missing_declaration():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = None

    block = blocks.StrfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "strf"
    mock_ctx.node.payload = None

    block = blocks.StrfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "strf"
    mock_ctx.node.payload = ""

    block = blocks.StrfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "strf"
    mock_ctx.node.payload = "     "

    block = blocks.StrfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_invalid_int_passing_isdigit_but_failing_int_conversion_is_rejected():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.declaration = "strf"
    mock_ctx.node.payload = "abc"
    # this passes isdigit but fails int-conversion because they're not ASCII 0-9
    mock_ctx.node.parameter = "²³"
    mock_ctx.interpret_segment = lambda x: x

    block = blocks.StrfBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_strf_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    # the mock_dt is used only indirectly because it mocks the datetime.now method used
    # by the StrfBlock internally
    # It is set up to return datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
    script = "{strf:%Y-%m-%d}"
    result = ts_interpreter.process(script).body
    assert result == "2000-01-01"


def test_dec_strf_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    fake_now_dt = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
    script = "{strf({user(timestamp)}):%c}"
    data = {"user": adapters.AttributeAdapter(MagicMock(created_at=fake_now_dt))}
    result = ts_interpreter.process(script, data).body
    assert result == "Sat Jan  1 00:00:00 2000"


def test_dec_strf_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(1735689600):%A %d, %B %Y}"
    result = ts_interpreter.process(script).body
    assert result == "Wednesday 01, January 2025"


def test_dec_strf_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T01:02:00.999):%H:%M %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "01:02 01-January-2025"


def test_dec_unix_docs_example_five(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    # the mock_dt is used only indirectly because it mocks the datetime.now method used
    # by the StrfBlock internally
    # It is set up to return datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
    script = "{unix}"
    result = ts_interpreter.process(script).body
    assert result == "946684800"


def test_dec_strf_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(1735689600):}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_strf_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(1735689600)}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_strf_invalid_parameter_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(invalid parameter stuff):%H:%M %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_strf_isoformat_with_micros_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T00:00:00.123456):%f}"
    result = ts_interpreter.process(script).body
    assert result == "123456"


def test_dec_strf_isoformat_without_millis_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T00:00:00):%H:%M %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "00:00 01-January-2025"


def test_dec_strf_isoformat_without_seconds_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T00:00):%H:%M %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "00:00 01-January-2025"


def test_dec_strf_isoformat_without_minutes_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T00):%H %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "00 01-January-2025"


def test_dec_strf_isoformat_without_time_component_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01):%d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "01-January-2025"


def test_dec_strf_isoformat_with_offset_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01T01:02:03+01:23):%H:%M%z}"
    result = ts_interpreter.process(script).body
    assert result == "01:02+0123"


def test_dec_strf_isoformat_space_separator_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(2025-01-01 00:00:00):%H:%M %d-%B-%Y}"
    result = ts_interpreter.process(script).body
    assert result == "00:00 01-January-2025"


def test_dec_strf_parameter_is_parsed(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf({my_var}):%Y-%m-%d}"
    data = {"my_var": adapters.StringAdapter("10 Jan 2025")}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-10"


def test_dec_strf_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{strf(24-12-2000 15:55):{my_var}}"
    data = {"my_var": adapters.StringAdapter("%d %B %Y @ %H:%M")}
    result = ts_interpreter.process(script, data).body
    assert result == "24 December 2000 @ 15:55"
