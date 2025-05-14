from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


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
            mock_dt.now.return_value = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
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
        mocked_dt.now.return_value = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
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
    mock_dt.now.return_value = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
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


def test_dec_timedelta_invalid_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta:This is not a datetime}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta:}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_param_with_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2025-08-01T01:02:03):}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_param_with_missing_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2025-08-01T01:02:03)}"
    result = ts_interpreter.process(script).body
    assert result == script


def test_dec_timedelta_invalid_param_is_replaced_by_utc_now(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta(This is not a datetime):1970-01-01T00:00:00+00:00}"
    mock_dt.now.return_value = datetime(2000, 1, 1, 0, 0, 5, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    # once for failing in str->dt conversion, returning None
    # once more for "if None use dt.now" in process method, following the above
    assert mock_dt.now.call_count == 2
    assert result == "30 years and 5 seconds ago"


def test_dec_timedelta_isoformat_without_millis_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2025-08-01T21:00:00):2024-08-01T01:23:45}"
    result = ts_interpreter.process(script).body
    assert result == "1 year, 19 hours, and 36 minutes ago"


def test_dec_timedelta_no_param_isoformat_without_millis_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01:23:45}"
    mock_dt.now.return_value = datetime(2030, 8, 1, 4, 23, 56, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "6 years, 3 hours, and 11 seconds ago"


def test_dec_timedelta_isoformat_without_seconds_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T11:53):2024-08-01T01:23}"
    result = ts_interpreter.process(script).body
    assert result == "10 hours and 30 minutes ago"


def test_dec_timedelta_no_param_isoformat_without_seconds_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01:23}"
    mock_dt.now.return_value = datetime(2050, 8, 1, 12, 1, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "26 years, 10 hours, and 38 minutes ago"


def test_dec_timedelta_isoformat_without_minutes_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T15):2024-08-01T01}"
    result = ts_interpreter.process(script).body
    assert result == "14 hours ago"


def test_dec_timedelta_no_param_isoformat_without_minutes_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01}"
    mock_dt.now.return_value = datetime(1984, 7, 31, 15, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "40 years and 10 hours"


def test_dec_timedelta_isoformat_without_time_component_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-26):2024-08-01}"
    result = ts_interpreter.process(script).body
    assert result == "25 days ago"


def test_dec_timedelta_no_param_isoformat_without_time_component_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2020-03-11}"
    mock_dt.now.return_value = datetime(2019, 11, 17, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "3 months and 23 days"


def test_dec_timedelta_isoformat_with_same_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T01:02:03+04:56):2024-08-01T12:02:03+04:56}"
    result = ts_interpreter.process(script).body
    assert result == "11 hours"


def test_dec_timedelta_no_param_isoformat_with_same_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T12:02:03+04:56}"
    fake_tz = timezone(timedelta(hours=4, minutes=56))
    mock_dt.now.return_value = datetime(2002, 8, 1, 1, 2, 3, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "22 years and 11 hours"


def test_dec_timedelta_isoformat_with_different_zones_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T14:28:03+07:30):2024-08-01T01:02:03+04:56}"
    result = ts_interpreter.process(script).body
    assert result == "10 hours and 52 minutes ago"


def test_dec_timedelta_no_param_isoformat_with_different_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01:02:03+04:56}"
    fake_tz = timezone(timedelta(hours=7, minutes=30))
    mock_dt.now.return_value = datetime(2010, 7, 31, 14, 35, 41, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "14 years, 13 hours, and 22 seconds"


def test_dec_timedelta_isoformat_with_same_negative_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T04:52:29-05:12):2024-08-01T01:02:03-05:12}"
    result = ts_interpreter.process(script).body
    assert result == "3 hours, 50 minutes, and 26 seconds ago"


def test_dec_timedelta_no_param_isoformat_with_same_negative_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01:02:03-05:12}"
    fake_tz = timezone(timedelta(hours=-5, minutes=-12))
    mock_dt.now.return_value = datetime(2024, 8, 1, 15, 22, 37, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "14 hours, 20 minutes, and 34 seconds ago"


def test_dec_timedelta_isoformat_with_different_negative_zones_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T04:52:29-13:12):2024-08-01T01:02:03-03:54}"
    result = ts_interpreter.process(script).body
    assert result == "13 hours, 8 minutes, and 26 seconds ago"


def test_dec_timedelta_no_param_isoformat_with_different_negative_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-08-01T01:02:03-03:54}"
    fake_tz = timezone(timedelta(hours=-13, minutes=-12))
    mock_dt.now.return_value = datetime(2022, 7, 31, 11, 2, 3, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "2 years, 4 hours, and 42 minutes"


def test_dec_timedelta_isoformat_with_mixed_zones_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-08-01T20:14:45+01:51):2024-05-02T19:01:33-14:06}"
    result = ts_interpreter.process(script).body
    assert result == "2 months, 29 days, and 9 hours ago"


def test_dec_timedelta_no_param_isoformat_with_different_zone_sign_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2017-10-07T19:01:33-14:06}"
    fake_tz = timezone(timedelta(hours=1, minutes=30))
    mock_dt.now.return_value = datetime(2017, 12, 23, 10, 37, 41, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "2 months, 15 days, and 8 seconds ago"


def test_dec_timedelta_isoformat_two_ordinal_dates_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-234T01:02:03+04:56):2024-133T01:02:03+04:56}"
    result = ts_interpreter.process(script).body
    assert result == "3 months and 9 days ago"


def test_dec_timedelta_no_param_isoformat_ordinal_date_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2024-133T01:02:03+04:56}"
    fake_tz = timezone(timedelta(hours=4, minutes=56))
    mock_dt.now.return_value = datetime(2024, 8, 21, 1, 2, 5, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "3 months, 9 days, and 2 seconds ago"


def test_dec_timedelta_isoformat_mixed_ordinal_and_normal_dates_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2024-012):2024-12-01T01:02:03+04:56}"
    result = ts_interpreter.process(script).body
    assert result == "10 months, 18 days, and 20 hours"


def test_dec_timedelta_time_only_without_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(14:54:11):02:49:54}"
    result = ts_interpreter.process(script).body
    assert result == "12 hours, 4 minutes, and 17 seconds ago"


def test_dec_timedelta_time_only_without_zone_on_one_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(14:54:11):02:49:54+12:30}"
    result = ts_interpreter.process(script).body
    assert result == "1 day, 34 minutes, and 17 seconds ago"


def test_dec_timedelta_no_param_time_only_without_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:02:49:54}"
    mock_dt.now.return_value = datetime(1975, 1, 1, 3, 59, 54, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 2
    assert result == "1 hour and 10 minutes ago"


def test_dec_timedelta_time_only_with_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(03:33:00+05:45):15:15:15+06:10}"
    result = ts_interpreter.process(script).body
    assert result == "11 hours, 17 minutes, and 15 seconds"


def test_dec_timedelta_no_param_time_only_with_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:15:15:15+06:10}"
    mock_dt.now.return_value = datetime(3000, 1, 2, 3, 33, 15, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 2
    assert result == "5 hours and 32 minutes"


def test_dec_timedelta_time_only_with_mixed_zones_are_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(01:11:11+14:00):15:51:15-12:30}"
    result = ts_interpreter.process(script).body
    assert result == "1 day, 17 hours, and 10 minutes"


def test_dec_timedelta_no_param_time_only_with_different_zone_sign_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:15:51:15-12:30}"
    fake_tz = timezone(timedelta(hours=14))
    mock_dt.now.return_value = datetime(2000, 1, 1, 23, 11, 11, tzinfo=fake_tz)
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 2
    assert result == "19 hours, 10 minutes, and 4 seconds"


def test_dec_timedelta_time_only_without_seconds_with_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(07:33+02:00):18:35-00:30}"
    result = ts_interpreter.process(script).body
    assert result == "13 hours and 32 minutes"


def test_dec_timedelta_no_param_time_only_without_seconds_with_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:18:35-00:30}"
    mock_dt.now.return_value = datetime(2025, 1, 1, 19, 10, 0, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 2
    assert result == "5 minutes ago"


def test_dec_timedelta_time_only_without_seconds_no_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(03:33):18:35}"
    result = ts_interpreter.process(script).body
    assert result == "15 hours and 2 minutes"


def test_dec_timedelta_no_param_time_only_without_seconds_no_zone_is_accepted(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:18:35}"
    mock_dt.now.return_value = datetime(2000, 1, 1, 3, 33, 15, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    assert mock_dt.now.call_count == 2
    assert result == "15 hours, 1 minute, and 45 seconds"


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
    mock_dt.now.return_value = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
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


def test_dec_timedelta_same_timestamps_return_0_seconds(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(2025-01-01T01:00:00+00:30):2025-01-01T00:30:00+00:00}"
    result = ts_interpreter.process(script).body
    assert result == "0 seconds"


def test_dec_timedelta_no_param_same_timestamps_return_0_seconds(
    ts_interpreter: TagScriptInterpreter,
    mock_dt: MagicMock,
):
    script = "{timedelta:2025-01-01T00:30:00+00:00}"
    mock_dt.now.return_value = datetime(2025, 1, 1, 0, 30, 0, tzinfo=timezone.utc)
    result = ts_interpreter.process(script).body
    mock_dt.now.assert_called_once()
    assert result == "0 seconds"


def test_dec_timedelta_single_unit_difference_works_properly(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(11:50):12:15}"
    result = ts_interpreter.process(script).body
    assert result == "25 minutes"


def test_dec_timedelta_single_unit_difference_works_properly_past_ver(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{timedelta(15:50):12:50}"
    result = ts_interpreter.process(script).body
    assert result == "3 hours ago"


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
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    assert result == "success"
