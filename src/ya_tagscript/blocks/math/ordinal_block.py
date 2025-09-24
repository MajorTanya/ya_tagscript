"""
Ordinal Abbreviation Block adapted from benz206's bTagScript, licensed under Creative
Commons Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/math_blocks.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class OrdinalBlock(BlockABC):
    """
    Returns the ordinal form of a number, including commas as thousands separators.

    If the payload is not a number, the block is rejected.

    If a parameter is provided, it must be one of the following:

    - ``c`` or ``comma``: Adds commas as thousands separators but no indicator
    - ``i`` or ``indicator``: Appends the ordinal indicator (e.g., ``st`` for 1st,
      ``nd`` for 2nd) but does not include commas as thousands separators

    **Usage**: ``{ord(["c"|"comma"|"i"|"indicator"]):<number>}``

    **Aliases**: ``o``, ``ord``

    **Parameter**: one of ``c``, ``comma``, ``i``, ``indicator`` (optional)

    **Payload**: ``number`` (required)

    **Examples**::

        {ord:1000}
        # Returns: 1,000th

        {ord(c):1213123}
        # Returns: 1,213,123

        {ord(i):2022}
        # Returns: 2022nd
    """

    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"o", "ord"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        parsed_payload = ctx.interpret_segment(payload)
        if not parsed_payload.isdigit():
            return None

        split = split_at_substring_zero_depth(parsed_payload, "-", max_split=1)
        num_str = split[-1]
        try:
            num = int(num_str)
        except ValueError:
            return None

        parameter = ctx.node.parameter if ctx.node.parameter is not None else ""
        parsed_param = ctx.interpret_segment(parameter)

        comma = f"{num:,}"
        if parsed_param.lower() in ["c", "comma"]:
            return comma

        # based on https://codegolf.stackexchange.com/a/4712
        # but de-golfed for readability
        indicator = "tsnrhtdd"[(num // 10 % 10 != 1) * (num % 10 < 4) * num % 10 :: 4]
        if parsed_param.lower() in ["i", "indicator"]:
            return f"{num}{indicator}"

        return f"{comma}{indicator}"
