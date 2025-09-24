from collections.abc import Callable
from datetime import UTC, datetime

from dateutil.parser import isoparse, parse
from dateutil.relativedelta import relativedelta

from ...interfaces import BlockABC
from ...interpreter import Context


class TimedeltaBlock(BlockABC):
    """
    This block calculates the difference between two datetime values and formats it
    into a human-readable string.

    The payload provides the "target" time, i.e. the time for which to calculate the
    distance from the "origin" time.

    The optional parameter provides the "origin" time, i.e. the time to use as a
    starting point for the calculation. When no parameter is provided, this defaults to
    the current date and time.

    Whether a date & time is provided via the parameter or payload will influence the
    direction of the calculation (i.e. whether the time difference is considered "in
    the past" or "in the future")

    The block supports ISO 8601 strings, timestamps, and other common datetime formats.
    If only a time is provided, it is assumed to be for the current UTC date.

    Formats may be mixed between the parameter and the payload.

    **Usage**: ``{timedelta(<origin datetime>):<target datetime>}``

    **Aliases**: ``timedelta``, ``td``

    **Parameter**: ``origin datetime`` (optional)

    **Payload**: ``target datetime`` (required)

    **Examples**::

        # All examples assume the default humanize function is used

        {timedelta(2025-01-01T00:00:00):30.01.2024}
        # 11 months and 2 days ago

        {timedelta:2024-08-31 00:00:00.000000+00:00}
        # 4 years, 7 months, and 30 days
        # (if the current UTC time was 2020-01-01T00:00:00)

        {timedelta(1735689600):946694800}
        # 24 years, 11 months, and 30 days ago
        # (1735689600 = Wed, 01 Jan 2025 00:00:00 +0000)
        # ( 946694800 = Sat, 01 Jan 2000 02:46:40 +0000)

        {timedelta(19:30):21:00}
        # 1 hour and 30 minutes
    """

    requires_nonempty_payload = True

    def __init__(
        self,
        time_humanize_fn: Callable[[datetime, datetime], str] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        time_humanize_fn : :class:`Callable[[datetime, datetime], str]` | :data:`None`
            A function that takes two :class:`~datetime.datetime` objects and returns
            a :class:`str` expressing the distance between the two.

            If set to :data:`None` (the default), an implementation using the
            `dateutil package <https://pypi.org/project/python-dateutil/>`_ and its
            :class:`~dateutil.relativedelta.relativedelta` is used which returns the
            three largest nonzero units of time in order. Example outputs may be:

                - 1 year
                - 4 months and 43 seconds
                - 9 days, 1 hour, and 8 seconds
        """
        if time_humanize_fn is not None:
            self._humanize_fn = time_humanize_fn
        else:
            self._humanize_fn = self._timedelta_humanize

    @property
    def _accepted_names(self) -> set[str]:
        return {"timedelta", "td"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        parsed_payload = ctx.interpret_segment(payload)
        target_dt = self._convert_str_to_datetime(parsed_payload)
        if target_dt is None:
            return None

        origin_dt = None
        if (param := ctx.node.parameter) is not None and param != "":
            parsed_param = ctx.interpret_segment(param)
            origin_dt = self._convert_str_to_datetime(parsed_param)

        if origin_dt is None:
            origin_dt = datetime.now(UTC)

        newer_fn = self._humanize_fn(target_dt, origin_dt)
        return newer_fn

    def _convert_str_to_datetime(self, input_str: str) -> datetime | None:
        if input_str.isdigit():
            # all numbers -> this is a UTC timestamp
            return datetime.fromtimestamp(int(float(input_str)), tz=UTC)
        else:
            try:
                dt = isoparse(input_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                return dt
            except ValueError:
                pass

            # This might be a time-only string, or a non-ISO date(time).
            # Assume "now" (UTC) as the baseline & let the parser update/replace
            # attributes as needed based on the input data.

            # Set the time parts to 0 to provide a sane default. Generally, if a unit
            # of time is not given in the input, it should be assumed as 0:
            # 18:35 means hour=18, minute=35, second=0, microsecond=0 (!)
            # If this was not done, the time components of "now" would be the default,
            # which is obviously undesirable.
            now = datetime.now(tz=UTC).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

            try:
                t = parse(input_str, default=now)
                return t.replace(tzinfo=now.tzinfo if t.tzinfo is None else t.tzinfo)
            except ValueError:
                pass

        return None

    def _timedelta_humanize(self, target_dt: datetime, origin_dt: datetime) -> str:
        attrs = ["years", "months", "days", "hours", "minutes", "seconds"]
        delta = relativedelta(target_dt, origin_dt)
        out_strs: list[str] = []
        is_past = False

        for a in attrs:
            value = getattr(delta, a, 0)
            if value != 0:
                unit = a if value not in (1, -1) else a.removesuffix("s")
                if value < 0:
                    is_past = True
                out_strs.append(f"{abs(value)} {unit}")

        suffix = " ago" if is_past else ""
        match len(out_strs):
            case 0:
                return "0 seconds"
            case 1:
                return out_strs[0] + suffix
            case 2:
                return f"{out_strs[0]} and {out_strs[1]}{suffix}"
            case _:
                return f"{out_strs[0]}, {out_strs[1]}, and {out_strs[2]}{suffix}"
