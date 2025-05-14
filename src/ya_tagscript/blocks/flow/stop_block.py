from ...exceptions import StopError
from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import parse_condition


class StopBlock(BlockABC):
    """
    This block stops tag processing if the provided parameter evaluates to true.

    If a payload is provided and the parameter condition evaluates to True, the payload
    will be returned as the response message. Otherwise, an empty string will be
    returned.

    Caution:
        Unlike the :class:`BreakBlock`, which continues processing, the
        :class:`StopBlock` **immediately** aborts all further processing *if its
        condition evaluates to* :data:`True` by means of raising an internal exception
        that is caught by the interpreter.

        This means no subsequent blocks will be interpreted and none of their side
        effects will occur. For example, a :class:`~ya_tagscript.blocks.CommandBlock`
        that comes after a triggered :class:`StopBlock` will **NOT** have its commands
        added to the :class:`~ya_tagscript.interpreter.Response`'s
        :attr:`~ya_tagscript.interpreter.Response.actions` attribute.

    **Usage**: ``{stop(<condition>):[message]}``

    **Aliases**: ``stop``, ``halt``, ``error``

    **Parameter**: ``condition`` (required)

    **Payload**: ``message`` (optional)

    **Examples**::

        {stop({args}==):You must provide arguments for this tag.}
        # Enforces providing arguments for a tag
    """

    requires_nonempty_parameter = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"stop", "halt", "error"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None

        if parse_condition(ctx, param):
            parsed_payload = ""
            if ctx.node.payload is not None:
                parsed_payload = ctx.interpret_segment(ctx.node.payload)
            raise StopError(parsed_payload)
        return ""
