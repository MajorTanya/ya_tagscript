from ...interfaces import BlockABC
from ...interpreter import Context


class PythonBlock(BlockABC):
    """
    This block supports string operations like containment, word matching, and
    positional indexing in the payload.

    Behaviour differs between aliases:

    - ``contains``: Checks if the parameter matches any word in the payload, split by
      whitespace.
    - ``in``: Checks if the parameter exists anywhere in the payload.
    - ``index``: Finds the position of the parameter in the payload, split by
      whitespace. If the parameter is not found, it returns -1.

    **Usage**: ``{contains(<string>):<payload>}``

    **Aliases**: ``contains``, ``in``, ``index``

    **Parameter**: ``string`` (required)

    **Payload**: ``payload`` (required)

    **Examples**::

        {contains(mute):How does it feel to be muted?}
        # false

        {contains(muted?):How does it feel to be muted?}
        # true

        {in(apple pie):banana pie apple pie and other pie}
        # true

        {in(mute):How does it feel to be muted?}
        # true

        {in(a):How does it feel to be muted?}
        # false

        {index(food.):I love to eat food. everyone does.}
        # 4

        {index(pie):I love to eat food. everyone does.}
        # -1

    .. versionchanged:: 1.3
        This block was moved from ``blocks.conditional`` to ``blocks.strings``.
        Users should import blocks by doing
        ``from ya_tagscript.blocks import PythonBlock`` so this change should affect
        very few users.
    """

    requires_any_parameter = True
    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"contains", "in", "index"}

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None:
            return None
        elif (param := ctx.node.parameter) is None:
            return None
        elif (payload := ctx.node.payload) is None:
            return None

        dec = ctx.interpret_segment(declaration).lower()
        parsed_param = ctx.interpret_segment(param)
        parsed_payload = ctx.interpret_segment(payload)

        if dec == "contains":
            return str(parsed_param in parsed_payload.split()).lower()
        elif dec == "in":
            return str(parsed_param in parsed_payload).lower()
        elif dec == "index":
            if parsed_param in (split := parsed_payload.split()):
                return str(split.index(parsed_param))
            else:
                return "-1"
        else:
            # not possible with will_accept filter before process, but
            # better safe than sorry
            return None
