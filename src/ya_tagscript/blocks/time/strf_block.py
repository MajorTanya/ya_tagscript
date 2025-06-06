from datetime import UTC, datetime

from dateutil.parser import isoparse, parse

from ...interfaces import BlockABC
from ...interpreter import Context


class StrfBlock(BlockABC):
    """
    This block formats dates and times using the provided format string.

    Behaviour differs between aliases:

    - ``unix``: Returns the current time as a seconds-resolution integer timestamp
    - ``strf``: Returns the current time (or time given in the parameter) formatted
      according to the format string in the payload

    The payload is the format string to be used with
    :meth:`~datetime.datetime.strftime`.

    See Also:
        Python's :mod:`datetime` documentation
            :meth:`~datetime.datetime.strftime`
            `Format Codes <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_

    Note:
        The ``unix`` alias *does not* take any format string payload and always returns
        the current Unix Epoch timestamp in seconds-resolution (i.e. seconds since
        1970-01-01 at 00:00:00 UTC).

    The parameter can be a timestamp or an ISO 8601 string. Many other common formats
    are supported as well but no exhaustive list can be provided. When in doubt, try it
    and see.

    If no parameter is provided, the block defaults to the current time.

    **Usage**: ``{strf(<parameter>):<format>}``

    **Aliases**: ``strf``, ``unix``

    **Parameter**: ``timestamp`` or ``datetime string`` (optional)

    **Payload**: ``format`` (required for ``strf``)

    **Examples**::

        {strf:%Y-%m-%d}
        # 2000-01-01

        {strf({user(timestamp)}):%c}
        # Sat Jan  1 00:00:00 2000

        {strf(1735689600):%A %d, %B %Y}
        # Wednesday 01, January 2025

        {strf(2025-01-01T01:02:00.999):%H:%M %d-%B-%Y}
        # 01:02 01-January-2025

        {unix}
        # 946684800
        # (this is 2000-01-01T00:00:00+00:00)
    """

    @property
    def _accepted_names(self) -> set[str]:
        return {"strf", "unix"}

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None:
            return None

        elif declaration == "unix":
            return str(int(datetime.now(UTC).timestamp()))

        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        elif (param := ctx.node.parameter) is not None and param != "":
            parsed_param = ctx.interpret_segment(param)
            if parsed_param.isdigit():
                try:
                    t = datetime.fromtimestamp(int(parsed_param), UTC)
                except ValueError:
                    return None
            else:
                try:
                    t = isoparse(parsed_param)
                except ValueError:
                    try:
                        t = parse(parsed_param)
                    except ValueError:
                        return None

        else:
            t = datetime.now(UTC)

        if t.tzinfo is None:
            t = t.replace(tzinfo=UTC)

        parsed_payload = ctx.interpret_segment(payload)
        return t.strftime(parsed_payload)
