from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class CycleBlock(BlockABC):
    """
    This block retrieves the element from the payload at the index specified by the
    parameter, looping around to the beginning of the payload if the index is out of
    bounds (roughly: ``index = index % len(payload)``).

    This block is 0-indexed (index 0 returns the first element) and allows for
    backwards indexing using negative values.

    The payload gets split on tilde (``~``) and each segment is interpreted separately
    before the value at the chosen index is retrieved and returned.

    Tildes are required to exist at ":term:`zero-depth`", i.e. only tildes present
    before interpretation will be used for splitting.

    **Usage**: ``{cycle(<number>):<payload>}``

    **Aliases**: ``cycle``

    **Parameter**: ``number`` (required)

    **Payload**: ``payload`` (required)

    **Examples**::

        {cycle(1):apple~banana~secret third thing}
        # banana
        {cycle(-3):apple~banana~secret third thing}
        # apple
        {cycle(10):apple~banana~secret third thing}
        # banana

        # Note how there are no zero-depth tildes in the payload, meaning the entire
        # payload is treated as a single item (assume {items} = "1st~2nd~3rd")
        {cycle(0):{items}}
        # 1st~2nd~3rd
    """

    requires_nonempty_parameter = True
    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"cycle"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None:
            return None

        parsed_param = ctx.interpret_segment(param)
        try:
            index = int(parsed_param)
        except ValueError:
            return "Could not parse cycle index"

        split = split_at_substring_zero_depth(payload, "~")
        haystack = [ctx.interpret_segment(h) for h in split]
        return haystack[index % len(haystack)]
