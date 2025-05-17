from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class ListBlock(BlockABC):
    """
    This block retrieves the element from the payload at the index specified by the
    parameter. If the index is out of bounds, it returns an empty string.

    This block is 0-indexed and allows for backwards indexing using negative values.

    Caution:
        The payload is interpreted in its entirety before it is split on tildes (``~``)
        and the entry at the provided index is returned. This means any blocks
        contained in the payload will be interpreted as well.

    **Usage**: ``{list(<number>):<payload>}``

    **Aliases**: ``list``

    **Parameter**: ``number`` (required)

    **Payload**: ``payload`` (required)

    **Examples**::

        {list(1):apple~banana~secret third thing}
        # banana
        {list(-2):apple~banana~secret third thing}
        # banana
        {list(10):apple~banana~secret third thing}
        # (empty string)

        # (assume {items} = "1st~2nd~3rd")
        {list(0):{items}}
        # 1st

    .. versionchanged:: 1.1
        The block no longer has a ":term:`zero-depth`" restriction (see Caution above)
    """

    requires_nonempty_parameter = True
    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"list"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None:
            return None

        parsed_param = ctx.interpret_segment(param)
        try:
            index = int(parsed_param)
        except ValueError:
            return "Could not parse list index"

        parsed_payload = ctx.interpret_segment(payload)
        split = split_at_substring_zero_depth(parsed_payload, "~")
        haystack = [ctx.interpret_segment(h) for h in split]
        return "" if (len(haystack) - 1) < index else haystack[index]
