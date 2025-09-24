from ...interfaces import BlockABC
from ...interpreter import Context
from ...interpreter.node import Node


class ShortcutRedirectBlock(BlockABC):
    """
    This block acts as a shortcut to redirect processing to another block.

    Specifically, this block behaves as if the number was passed as the parameter to
    the other block (see examples). The ``declaration`` must be a number, any other
    ``declaration`` will be rejected.

    **Usage**: ``{<number>}``

    **Aliases**: N/A

    **Parameter**: ``None``

    **Payload**: ``None``

    **Examples**::

        # (Python) With a ShortcutRedirectBlock defined and provided to an interpreter instance as such:
        ShortcutRedirectBlock("args")

        # (TagScript) this block redirects to the "args" variable which contains "hello world"
        {1}
        # hello

        # (TagScript) this is a shortcut to the functionally identical version:
        {args(1)}
        # hello
    """

    def __init__(self, shortcut_for: str) -> None:
        self.redirect_name = shortcut_for

    @property
    def _accepted_names(self) -> None:
        return None

    def will_accept(self, ctx: Context) -> bool:
        """
        The implementation differs from the base
        :meth:`~ya_tagscript.interfaces.BlockABC.will_accept` method due to this
        block's unique behaviour. A :class:`~ya_tagscript.interfaces.NodeABC` is only
        acceptable if its (interpreted) declaration consists only of numbers.
        """
        if (declaration := ctx.node.declaration) is None:
            return False
        parsed_declaration = ctx.interpret_segment(declaration)
        return parsed_declaration.isdigit()

    def process(self, ctx: Context) -> str | None:
        redirect_block_node = Node.block(
            declaration=self.redirect_name,
            parameter=ctx.node.declaration,
            payload=None,
        )
        return ctx.interpret_segment(redirect_block_node.as_raw_string())
