from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context


class JoinBlock(BlockABC):
    """
    This block replaces spaces in the payload with the provided separator.

    If the parameter is missing, the block will be rejected.

    To use this block as a pseudo-concatenation block, include the parentheses with no
    content between them (see examples below).

    **Usage**: ``{join(<separator>):<text>}``

    **Aliases**: ``join``

    **Parameter**: ``separator`` (required; can be empty)

    **Payload**: ``text`` (required)

    **Examples**::

        {join(.):Dot notation is funky}
        # Dot.notation.is.funky

        {join():I can masquerade as a concat block}
        # Icanmasqueradeasaconcatblock
    """

    _VALID_NAMES = {"join"}

    requires_any_parameter = True
    requires_any_payload = True

    def process(self, ctx: Context) -> str | None:
        param = ctx.node.parameter
        if param is None:
            return None

        payload = ctx.node.payload
        if payload is None:
            return None

        parsed_parameter = ctx.interpret_segment(param)
        parsed_payload = ctx.interpret_segment(payload)

        return parsed_payload.replace(" ", parsed_parameter)
