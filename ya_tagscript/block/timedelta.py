from datetime import datetime, timedelta, timezone
from typing import Optional, Callable

from ..interface import verb_required_block
from ..interpreter import Context


class TimedeltaBlock(verb_required_block(True, payload=True)):
    """
    The timedelta block calculates the difference between two datetime strings in the
    format 'YYYY-mm-dd HH:MM:SS.ffffff+HH:MM'.
    If only one datetime string is provided, it calculates the difference between that
    datetime and now.

    The output is a human-readable string that represents the difference between the
    two datetimes with the three largest non-zero units of time (years, months, days,
    hours, minutes, seconds).

    Users can optionally supply a different time humanizing function when adding the
    TimedeltaBlock to the Interpreter instance being used to parse scripts. This
    function must take a ``datetime.timedelta`` instance and return a ``str``.

    **Usage:** ``{td(<later_datetime>):<earlier_datetime>}`` or ``{td:<datetime>}``

    **Examples:** ::

        {td(2024-08-31 00:00:00.000000+00:00):2020-01-01 00:00:00.000000+00:00}
        # 4 years, 7 months, 30 days

        {td:2024-08-31 00:00:00.000000+00:00}
        # (current time - 2024-08-31 00:00:00.000000+00:00)

    """

    ACCEPTED_NAMES = ("timedelta", "td")
    _DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"

    def __init__(
        self,
        time_humanize_fn: Callable[[timedelta], str] | None = None,
    ):
        if time_humanize_fn is not None:
            self.humanize_fn = time_humanize_fn
        else:
            self.humanize_fn = _timedelta_humanize

    def process(self, ctx: Context) -> Optional[str]:
        earlier_dt_str = ctx.verb.payload
        later_dt_str = ctx.verb.parameter

        try:
            if earlier_dt_str:
                earlier_dt = datetime.strptime(earlier_dt_str, self._DATETIME_FORMAT)
            elif later_dt_str:
                earlier_dt = datetime.strptime(later_dt_str, self._DATETIME_FORMAT)
                later_dt_str = None
            else:
                return None

            if later_dt_str:
                later_dt = datetime.strptime(later_dt_str, self._DATETIME_FORMAT)
            else:
                later_dt = datetime.now(tz=timezone.utc)
        except ValueError:
            return None

        return self.humanize_fn(earlier_dt - later_dt)


def _timedelta_humanize(delta: timedelta) -> str:
    """
    Converts a timedelta object into a human-readable string.

    :param delta: The timedelta object to convert.
    :return: A human-readable string representing the timedelta.

    **Notes:**

    - When the timedelta is negative, the string will end with "ago".
    - The string will only contain the three largest components.
    - The components are ordered as years, months, days, hours, minutes, seconds.
    - The component names are pluralised when their value is larger 1.
    - Weeks are not included.
    """
    seconds_in_minute = 60
    seconds_in_hour = 60 * seconds_in_minute
    seconds_in_day = 24 * seconds_in_hour
    seconds_in_week = 7 * seconds_in_day
    seconds_in_year = 365.2425 * seconds_in_day
    seconds_in_month = seconds_in_year // 12
    days_in_week = 7

    total_seconds = delta.total_seconds()
    time_suffix = "ago" if total_seconds <= 0 else ""
    total_seconds = abs(total_seconds)
    years, rem = divmod(total_seconds, seconds_in_year)
    months, rem = divmod(rem, seconds_in_month)
    weeks, rem = divmod(rem, seconds_in_week)
    days, rem = divmod(rem, seconds_in_day)
    hours, rem = divmod(rem, seconds_in_hour)
    minutes, rem = divmod(rem, seconds_in_minute)
    seconds, _ = divmod(rem, 1)
    components: dict[str, int] = {
        "year": int(years),
        "month": int(months),
        "day": int(days) + int(weeks * days_in_week),
        "hour": int(hours),
        "minute": int(minutes),
        "second": int(seconds),
    }

    out = ""
    num_components = 0
    for c in components.items():
        if c[1] in (0, -1):
            continue
        out += f"{c[1]} {c[0] if c[1] == 1 else (c[0] + "s")}, "
        if (num_components := num_components + 1) == 3:
            break

    return f"{", and ".join(out.strip().removesuffix(",").rsplit(", ", 1))} {time_suffix}".strip()
