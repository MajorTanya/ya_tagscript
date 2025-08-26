from collections.abc import Callable
from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter

_MINUS_13_12_TZ = timezone(timedelta(hours=-13, minutes=-12))
_MINUS_5_12_TZ = timezone(timedelta(hours=-5, minutes=-12))
_PLUS_1_30_TZ = timezone(timedelta(hours=1, minutes=30))
_PLUS_4_56_TZ = timezone(timedelta(hours=4, minutes=56))
_PLUS_7_30_TZ = timezone(timedelta(hours=7, minutes=30))
_PLUS_14_TZ = timezone(timedelta(hours=14))


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.TimedeltaBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


@pytest.fixture
def mock_dt():
    """
    Provides a MagicMock with a datetime.datetime spec mocked to return
    2000-01-01T00:00:00+00:00 when calling the datetime.datetime.now() method.

    Notes
    -----
    Using tests are free to modify the return value of the now method, e.g.::

        def test_other_datetime(interpreter: TagScriptInterpreter, mock_dt: MagicMock):
            mock_dt.now.return_value = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
            # ... proceed with tests
    """
    # Note: We patch the datetime.datetime object so we can mock the return value of
    # datetime.now when testing no-param uses of the Timedelta block (which indicates a
    # fallback to datetime.now @ UTC)
    with patch(
        "ya_tagscript.blocks.time.timedelta_block.datetime",
        spec=datetime,
        wraps=datetime,
    ) as mocked_dt:
        mocked_dt.now.return_value = datetime(2000, 1, 1, 0, 0, 0, tzinfo=UTC)
        yield mocked_dt


@pytest.fixture
def custom_humanize_fn():
    return MagicMock(Callable[[datetime, datetime], str], return_value="success")


@pytest.fixture
def ts_interpreter_with_custom_humanize_fn_in_td_block(
    custom_humanize_fn: Callable[[datetime, datetime], str],
):
    b = [
        blocks.TimedeltaBlock(custom_humanize_fn),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.TimedeltaBlock()
    assert block._accepted_names == {"timedelta", "td"}


def test_process_method_rejects_missing_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = None

    block = blocks.TimedeltaBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_empty_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = ""

    block = blocks.TimedeltaBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_process_method_rejects_whitespace_only_payload():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.payload = "     "

    block = blocks.TimedeltaBlock()
    returned = block.process(mock_ctx)
    assert returned is None


def test_dec_timedelta_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2025-01-01T00:00:00):30.01.2024}"
    result = ts_interpreter.process(script).body
    assert result == "11 months and 2 days ago"


def test_dec_timedelta_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-31 00:00:00.000000+00:00}"
    mock_dt.now.return_value = datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "4 years, 7 months, and 30 days"


def test_dec_timedelta_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(1735689600):946694800}"
    result = ts_interpreter.process(script).body
    assert result == "24 years, 11 months, and 30 days ago"


def test_dec_timedelta_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(19:30):21:00}"
    result = ts_interpreter.process(script).body
    assert result == "1 hour and 30 minutes"


@pytest.mark.parametrize(
    "script",
    (
        pytest.param("{timedelta}", id="missing_payload"),
        pytest.param("{timedelta:}", id="empty_payload"),
        pytest.param("{timedelta:This is not a datetime}", id="invalid_payload"),
        pytest.param("{timedelta(2025-08-01T01:02:03):}", id="param_empty_payload"),
        pytest.param("{timedelta(2025-08-01T01:02:03)}", id="param_missing_payload"),
    ),
)
def test_dec_timedelta_invalid_inputs_are_rejected(
    script: str,
    ts_interpreter: TagScriptInterpreter,
):
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_invalid_param_is_replaced_by_utc_now(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta(This is not a datetime):1970-01-01T00:00:00+00:00}"
    mock_dt.now.return_value = datetime(2000, 1, 1, 0, 0, 5, tzinfo=UTC)
    result = ts_interpreter.process(script).body
    # once for failing in str->dt conversion, returning None
    # once more for "if None use dt.now" in process method, following the above
    assert mock_dt.now.call_count == 2
    assert result == "30 years and 5 seconds ago"


@pytest.mark.parametrize(
    ("script", "out"),
    (
        pytest.param(
            "{timedelta(2025-08-01T21:00:00):2024-08-01T01:23:45}",
            "1 year, 19 hours, and 36 minutes ago",
            id="no_millis",
        ),
        pytest.param(
            "{timedelta(2024-08-01T11:53):2024-08-01T01:23}",
            "10 hours and 30 minutes ago",
            id="no_seconds",
        ),
        pytest.param(
            "{timedelta(2024-08-01T15):2024-08-01T01}",
            "14 hours ago",
            id="no_minutes",
        ),
        pytest.param(
            "{timedelta(2024-08-26):2024-08-01}",
            "25 days ago",
            id="no_time_component",
        ),
        pytest.param(
            "{timedelta(2024-08-01T01:02:03+04:56):2024-08-01T12:02:03+04:56}",
            "11 hours",
            id="same_offsets",
        ),
        pytest.param(
            "{timedelta(2024-08-01T14:28:03+07:30):2024-08-01T01:02:03+04:56}",
            "10 hours and 52 minutes ago",
            id="different_offsets",
        ),
        pytest.param(
            "{timedelta(2024-08-01T04:52:29-05:12):2024-08-01T01:02:03-05:12}",
            "3 hours, 50 minutes, and 26 seconds ago",
            id="same_negative_offset",
        ),
        pytest.param(
            "{timedelta(2024-08-01T04:52:29-13:12):2024-08-01T01:02:03-03:54}",
            "13 hours, 8 minutes, and 26 seconds ago",
            id="different_negative_offsets",
        ),
        pytest.param(
            "{timedelta(2024-08-01T20:14:45+01:51):2024-05-02T19:01:33-14:06}",
            "2 months, 29 days, and 9 hours ago",
            id="mixed_offsets",
        ),
        pytest.param(
            "{timedelta(2024-234T01:02:03+04:56):2024-133T01:02:03+04:56}",
            "3 months and 9 days ago",
            id="two_ordinal_dates",
        ),
        pytest.param(
            "{timedelta(2024-012):2024-12-01T01:02:03+04:56}",
            "10 months, 18 days, and 20 hours",
            id="mixed_date_types",
        ),
        pytest.param(
            "{timedelta(2025-01-01T01:00:00+00:30):2025-01-01T00:30:00+00:00}",
            "0 seconds",
            id="same_timestamp_returns_0_seconds",
        ),
    ),
)
def test_dec_timedelta_basic_isoformat(
    script: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    result = ts_interpreter.process(script).body
    assert result == out


@pytest.mark.parametrize(
    ("script", "out"),
    (
        pytest.param(
            "{timedelta(14:54:11):02:49:54}",
            "12 hours, 4 minutes, and 17 seconds ago",
            id="normal",
        ),
        pytest.param(
            "{timedelta(03:33):18:35}",
            "15 hours and 2 minutes",
            id="no_seconds",
        ),
        pytest.param(
            "{timedelta(14:54:11):02:49:54+12:30}",
            "1 day, 34 minutes, and 17 seconds ago",
            id="one_offset",
        ),
        pytest.param(
            "{timedelta(03:33:00+05:45):15:15:15+06:10}",
            "11 hours, 17 minutes, and 15 seconds",
            id="different_offsets",
        ),
        pytest.param(
            "{timedelta(01:11:11+14:00):15:51:15-12:30}",
            "1 day, 17 hours, and 10 minutes",
            id="mixed_offsets",
        ),
        pytest.param(
            "{timedelta(07:33+02:00):18:35-00:30}",
            "13 hours and 32 minutes",
            id="no_seconds_different_offsets",
        ),
        pytest.param(
            "{timedelta(11:50):12:15}",
            "25 minutes",
            id="single_unit_future",
        ),
        pytest.param(
            "{timedelta(15:50):12:50}",
            "3 hours ago",
            id="single_unit_past",
        ),
    ),
)
def test_dec_timedelta_basic_time_only(
    script: str,
    out: str,
    ts_interpreter: TagScriptInterpreter,
):
    result = ts_interpreter.process(script).body
    assert result == out


@pytest.mark.parametrize(
    ("payload", "fake_now_dt", "out"),
    (
        pytest.param(
            "2024-08-01T01:23:45",
            datetime(2030, 8, 1, 4, 23, 56, tzinfo=UTC),
            "6 years, 3 hours, and 11 seconds ago",
            id="no_millis",
        ),
        pytest.param(
            "2024-08-01T01:23",
            datetime(2050, 8, 1, 12, 1, tzinfo=UTC),
            "26 years, 10 hours, and 38 minutes ago",
            id="no_seconds",
        ),
        pytest.param(
            "2024-08-01T01",
            datetime(1984, 7, 31, 15, tzinfo=UTC),
            "40 years and 10 hours",
            id="no_minutes",
        ),
        pytest.param(
            "2020-03-11",
            datetime(2019, 11, 17, tzinfo=UTC),
            "3 months and 23 days",
            id="no_time",
        ),
        pytest.param(
            "2024-08-01T12:02:03+04:56",
            datetime(2002, 8, 1, 1, 2, 3, tzinfo=_PLUS_4_56_TZ),
            "22 years and 11 hours",
            id="same_offset",
        ),
        pytest.param(
            "2024-08-01T01:02:03+04:56",
            datetime(2010, 7, 31, 14, 35, 41, tzinfo=_PLUS_7_30_TZ),
            "14 years, 13 hours, and 22 seconds",
            id="different_offsets",
        ),
        pytest.param(
            "2024-08-01T01:02:03-05:12",
            datetime(2024, 8, 1, 15, 22, 37, tzinfo=_MINUS_5_12_TZ),
            "14 hours, 20 minutes, and 34 seconds ago",
            id="same_negative_offset",
        ),
        pytest.param(
            "2024-08-01T01:02:03-03:54",
            datetime(2022, 7, 31, 11, 2, 3, tzinfo=_MINUS_13_12_TZ),
            "2 years, 4 hours, and 42 minutes",
            id="different_negative_offsets",
        ),
        pytest.param(
            "2017-10-07T19:01:33-14:06",
            datetime(2017, 12, 23, 10, 37, 41, tzinfo=_PLUS_1_30_TZ),
            "2 months, 15 days, and 8 seconds ago",
            id="mixed_offsets",
        ),
        pytest.param(
            "2024-133T01:02:03+04:56",
            datetime(2024, 8, 21, 1, 2, 5, tzinfo=_PLUS_4_56_TZ),
            "3 months, 9 days, and 2 seconds ago",
            id="ordinal_date_same_offset",
        ),
        pytest.param(
            "2025-01-01T00:30:00+00:00",
            datetime(2025, 1, 1, 0, 30, 0, tzinfo=UTC),
            "0 seconds",
            id="same_timestamp_returns_0_seconds",
        ),
    ),
)
def test_dec_timedelta_no_param_isoformat(
    payload: str,
    fake_now_dt: datetime,
    out: str,
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = f"{{timedelta:{payload}}}"
    mock_dt.now.return_value = fake_now_dt
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 1
    assert result == out


@pytest.mark.parametrize(
    ("script", "fake_now_dt", "out"),
    (
        pytest.param(
            "{timedelta:02:49:54}",
            datetime(1975, 1, 1, 3, 59, 54, tzinfo=UTC),
            "1 hour and 10 minutes ago",
            id="no_offset",
        ),
        pytest.param(
            "{timedelta:15:15:15+06:10}",
            datetime(3000, 1, 2, 3, 33, 15, tzinfo=UTC),
            "5 hours and 32 minutes",
            id="different_offset",
        ),
        pytest.param(
            "{timedelta:15:51:15-12:30}",
            datetime(2000, 1, 1, 23, 11, 11, tzinfo=_PLUS_14_TZ),
            "19 hours, 10 minutes, and 4 seconds",
            id="mixed_offsets",
        ),
        pytest.param(
            "{timedelta:18:35-00:30}",
            datetime(2025, 1, 1, 19, 10, 0, tzinfo=UTC),
            "5 minutes ago",
            id="no_seconds_with_negative_offset",
        ),
        pytest.param(
            "{timedelta:18:35}",
            datetime(2000, 1, 1, 3, 33, 15, tzinfo=UTC),
            "15 hours, 1 minute, and 45 seconds",
            id="no_seconds_no_offset",
        ),
    ),
)
def test_dec_timedelta_no_param_time_only(
    script: str,
    fake_now_dt: datetime,
    out: str,
    mock_dt: MagicMock,
    ts_interpreter: TagScriptInterpreter,
):
    mock_dt.now.return_value = fake_now_dt
    result = ts_interpreter.process(script).body
    # once to add date info to payload, once to get "now" for no-param
    assert mock_dt.now.call_count == 2
    assert result == out


def test_dec_timedelta_utc_timestamps_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(1234567890):987654321}"
    result = ts_interpreter.process(script).body
    assert result == "7 years, 9 months, and 24 days ago"
    # make sure the timestamps got parsed correctly
    script2 = "{timedelta(2009-02-13T23:31:30+00:00):2001-04-19T04:25:21+00:00}"
    result2 = ts_interpreter.process(script2).body
    assert result2 == "7 years, 9 months, and 24 days ago"
    assert result == result2


def test_dec_timedelta_no_param_utc_timestamp_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:1010101010}"
    mock_dt.now.return_value = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    result = ts_interpreter.process(script).body
    assert result == "22 years, 11 months, and 28 days ago"
    # make sure the timestamps got parsed correctly
    script2 = "{timedelta:2002-01-03T23:36:50+00:00}"
    result2 = ts_interpreter.process(script2).body
    assert result2 == "22 years, 11 months, and 28 days ago"
    assert result == result2


def test_dec_timedelta_timestamp_and_normal_datetime_can_be_combined(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(1010101010):2002-01-03T03:41:16+00:00}"
    result = ts_interpreter.process(script).body
    assert result == "19 hours, 55 minutes, and 34 seconds ago"
    # make sure the timestamp got parsed correctly
    script2 = "{timedelta(2002-01-03T23:36:50+00:00):2002-01-03T03:41:16+00:00}"
    result2 = ts_interpreter.process(script2).body
    assert result2 == "19 hours, 55 minutes, and 34 seconds ago"
    assert result == result2


def test_dec_timedelta_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta({my_var}):10:00}"
    data = {"my_var": adapters.StringAdapter("12:00")}
    result = ts_interpreter.process(script, data).body
    assert result == "2 hours ago"


def test_dec_timedelta_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(14:50):{my_var}}"
    data = {"my_var": adapters.StringAdapter("14:45:30")}
    result = ts_interpreter.process(script, data).body
    assert result == "4 minutes and 30 seconds ago"


def test_dec_timedelta_custom_humanize_fn_is_called_once(
    ts_interpreter_with_custom_humanize_fn_in_td_block: TagScriptInterpreter,
    custom_humanize_fn: MagicMock,
):
    ts_interpreter = ts_interpreter_with_custom_humanize_fn_in_td_block
    # just super basic "does this get called and returned properly" testing to make
    # sure it actually works as intended
    script = "{timedelta(2025-01-01):2024-01-01}"
    result = ts_interpreter.process(script).body
    custom_humanize_fn.assert_called_once_with(
        datetime(2024, 1, 1, tzinfo=UTC),
        datetime(2025, 1, 1, tzinfo=UTC),
    )
    assert result == "success"
