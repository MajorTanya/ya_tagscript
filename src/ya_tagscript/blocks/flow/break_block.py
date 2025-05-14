from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import parse_condition


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

    requires_any_parameter = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"break", "short", "shortcircuit"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None:
            return None

        if (condition_fulfilled := parse_condition(ctx, param)) is None:
            return ""
        elif condition_fulfilled:
            payload = ""
            if ctx.node.payload is not None:
                payload = ctx.interpret_segment(ctx.node.payload)
            ctx.response.body = payload
        return ""
