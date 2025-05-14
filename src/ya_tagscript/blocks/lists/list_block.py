from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class ListBlock(BlockABC):
    """
    This block retrieves the element from the payload at the index specified by the
    parameter. If the index is out of bounds, it returns an empty string.

    This block is 0-indexed and allows for backwards indexing using negative values.

    The payload gets split on tilde (``~``), and each segment is interpreted separately
    before the value at the chosen index is retrieved and returned.

    Tildes are required to exist at ":term:`zero-depth`", i.e. only tildes present
    before interpretation will be used for splitting.

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

        # Note how there are no zero-depth tildes in the payload, meaning the entire
        # payload is treated as a single item (assume {items} = "1st~2nd~3rd")
        {list(0):{items}}
        # 1st~2nd~3rd
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

        split = split_at_substring_zero_depth(payload, "~")
        haystack = [ctx.interpret_segment(h) for h in split]
        return "" if (len(haystack) - 1) < index else haystack[index]
