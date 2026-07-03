from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context


class SilenceBlock(BlockABC):
    """
    Signal to suppress the output of command blocks in this script. This should not
    affect the normal output of the script.

    This block may be placed anywhere in a script.

    The block is idempotent, so it only needs to be used once. Additional uses have the
    same effect of setting the "silent" actions key to :data:`True`.

    There is no way to "unset" this key once a silence block has been used.

    **Usage**: ``{silent}``

    **Aliases**: ``silent``, ``silence``

    **Parameter**: ``None``

    **Payload**: ``None``

    **Examples**::

        {silent}
        # Signals to suppress the outputs of all command blocks in the script

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["silent"]``: :class:`Literal[True]` — Always :data:`True` if a
          SilenceBlock was used
        - The key is available via the
          :attr:`SilenceBlock.ACTIONS_KEY
          <ya_tagscript.blocks.SilenceBlock.ACTIONS_KEY>` class attribute

    Note:
        This block will only set the ``silent``
        :attr:`~ya_tagscript.interpreter.Response.actions` key to :data:`True`. It is
        *up to the client* to implement actual silencing behaviour for command block
        outputs. A client may also choose to let the block affect normal output but
        this is **not** recommended.
    """

    ACTIONS_KEY = "silent"
    """
    The key used to store data in the
    :attr:`Response.actions <ya_tagscript.interpreter.Response.actions>`.

    .. versionadded:: 1.7.1
    """

    _VALID_NAMES = {"silent", "silence"}

    def process(self, ctx: Context) -> str | None:
        ctx.response.actions[SilenceBlock.ACTIONS_KEY] = True
        return ""
