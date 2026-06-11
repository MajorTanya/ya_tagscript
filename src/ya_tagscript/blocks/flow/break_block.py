from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context
from ya_tagscript.util import parse_condition


class BreakBlock(BlockABC):
    """
    This block forces the tag output to only include the payload of this block if the
    provided condition evaluates to true. If no payload is provided, the tag output
    will be empty.

    Caution:
        Unlike the :class:`StopBlock`, which halts all TagScript processing and returns
        its message, the :class:`BreakBlock` *continues the processing of subsequent
        blocks*.

        This means all subsequent blocks may still result in their side effects (if
        any). For example, a :class:`~ya_tagscript.blocks.CommandBlock` that follows a
        triggered :class:`BreakBlock` will still cause the command to be listed in the
        ``"commands"`` key of the :class:`~ya_tagscript.interpreter.Response`'s
        :attr:`~ya_tagscript.interpreter.Response.actions` attribute, which could cause
        erroneous command execution by a consuming client.

    **Usage**: ``{break(<condition>):[message]}``

    **Aliases**: ``break``, ``short``, ``shortcircuit``

    **Parameter**: ``condition`` (required)

    **Payload**: ``message`` (optional)

    **Examples**::

        {break({args}==):You did not provide any input.}
    """

    _VALID_NAMES = {"break", "short", "shortcircuit"}

    requires_any_parameter = True

    def process(self, ctx: Context) -> str | None:
        param = ctx.node.parameter
        if param is None:
            return None

        condition_fulfilled = parse_condition(ctx, param)
        if condition_fulfilled is None:
            return ""
        elif condition_fulfilled:
            payload = ""
            if ctx.node.payload is not None:
                payload = ctx.interpret_segment(ctx.node.payload)
            ctx.response.body = payload
        return ""
