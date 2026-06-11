import re

from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context

_RANGE_PATTERN = re.compile(r"(?P<lower>-?\d+)(?:-(?P<upper>-?\d+))?")


class SubstringBlock(BlockABC):
    """
    This block extracts a substring from the payload based on the parameter.

    The parameter specifies the start and end indices of the substring, separated by a
    hyphen (``-``). The starting index is inclusive and the ending index is exclusive.

    If only one index is provided, the rest of the payload is returned starting from
    this index.

    This block is 0-indexed. Negative indices are supported.

    Note:
        The indices behave like normal Python slices. That means an index that is too
        large will return an empty string and an index that is too negative will return
        the entire string (see examples below).

    **Usage**: ``{substring(<start>-<end>):<text>}``

    **Aliases**: ``substring``, ``substr``

    **Parameter**: ``<start>`` OR ``<start>-<end>`` (both numbers) (required)

    **Payload**: ``text`` (required)

    **Examples**::

        {substring(1-4):testing}
        # est

        {substring(6):hello world}
        # world

        {substring(100):hello world}
        # (an empty string is returned)

        {substring(-100):hello world}
        # hello world
    """

    _VALID_NAMES = {"substring", "substr"}

    requires_nonempty_parameter = True
    requires_nonempty_payload = True

    def process(self, ctx: Context) -> str | None:
        param = ctx.node.parameter
        if param is None or param.strip() == "":
            return None

        payload = ctx.node.payload
        if payload is None or payload.strip() == "":
            return None

        parsed_param = ctx.interpret_segment(param)
        parsed_payload = ctx.interpret_segment(payload)

        found_range = re.fullmatch(_RANGE_PATTERN, parsed_param)
        if found_range is None:
            return None

        # try/except not needed for:
        # - IndexError because slices don't raise it
        # - ValueError because the regex used has only digits, which can be int-parsed
        if found_range.group("upper") is None:
            start_idx = int(found_range.group("lower"))
            return parsed_payload[start_idx:]
        else:
            start_idx = int(found_range.group("lower"))
            end_idx = int(found_range.group("upper"))
            return parsed_payload[start_idx:end_idx]
