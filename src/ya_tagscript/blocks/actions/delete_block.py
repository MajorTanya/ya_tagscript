"""
DeleteBlock adapted from benz206's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/discord_blocks/delete_block.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import parse_condition


class DeleteBlock(BlockABC):
    """
    Signal that the input message should be deleted.

    If no expression is provided (just ``{delete}`` is used), it will always signal
    that the message should be deleted.

    If an expression is provided, it is processed. If it evaluates to be True, the
    block will signal that the message should be deleted.

    The block is idempotent, i.e. only one is ever needed for a given script. Once one
    block has set the "delete" actions key, subsequent copies are ignored, even if they
    provide other expressions with a different outcome.

    **Usage**: ``{delete(<expression>)}``

    **Aliases**: ``delete``, ``del``

    **Parameter**: ``expression`` (optional)

    **Payload**: ``None``

    **Examples**::

        {delete}
        {del(true==true)}

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["delete"]``: :class:`bool` — Whether the invoking message should be
          deleted

    Note:
        This block will only set the ``delete``
        :attr:`~ya_tagscript.interpreter.Response.actions` key to
        :data:`True`/:data:`False`. It is *up to the client* to implement actual
        deletion behaviour as desired.
    """

    @property
    def _accepted_names(self) -> set[str]:
        return {"delete", "del"}

    def process(self, ctx: Context) -> str | None:
        value: bool | None
        if "delete" in ctx.response.actions.keys():
            return ""
        elif (param := ctx.node.parameter) is None:
            value = True
        else:
            value = parse_condition(ctx, param)
        ctx.response.actions["delete"] = value
        return ""
