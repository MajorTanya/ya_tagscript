from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context
from ya_tagscript.util import split_at_substring_zero_depth


class ReplaceBlock(BlockABC):
    """
    This block replaces all occurrences of a substring in the payload with another
    substring.

    The substring to replace and its replacement are provided as a comma-separated pair
    in the parameter. If ``new`` is omitted or empty, the substring will be removed.

    The ``old`` substring is case-sensitive, e.g. ``A`` is not replaced if ``old`` is
    ``a``, etc.

    **Usage**: ``{replace(<old>,<new>):<text>}``

    **Aliases**: ``replace``

    **Parameter**: ``old`` OR ``old,new`` (required; ``new`` can be empty)

    **Payload**: ``text`` (required)

    **Examples**::

        {replace(o,i):welcome to the server}
        # welcime ti the server

        {replace(1,6):{args}}
        # if {args} is 1234567
        # 6234567

        {replace(, ):Test}
        # T e s t

        {replace(an):An amazing Canadian banana}
        # An amazing Cadi ba
    """

    _VALID_NAMES = {"replace"}

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
        split_param = split_at_substring_zero_depth(parsed_param, ",", max_split=1)
        if len(split_param) == 1:
            old = ctx.interpret_segment(split_param[0])
            new = ""
        else:
            old = ctx.interpret_segment(split_param[0])
            new = ctx.interpret_segment(split_param[1])

        parsed_payload = ctx.interpret_segment(payload)
        return parsed_payload.replace(old, new)
