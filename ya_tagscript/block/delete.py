"""
DeleteBlock copied from Leg3ndary's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/Leg3ndary/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/discord_blocks/delete_block.py
"""

from typing import Optional

from .helpers import helper_parse_if
from ..interface import Block
from ..interpreter import Context


class DeleteBlock(Block):
    """
    The delete block will delete the message if the condition provided in
    the parameter is met, or if just the block is added, the message will
    be deleted. Only one delete block will be processed, the rest,
    removed, but ignored.

    .. note::

        This block will only set the actions "delete" key to True/False.
        You must set the behaviour manually.

    **Usage:** ``{delete(<expression>)}``

    **Aliases:** ``del``

    **Payload:** ``None``

    **Parameter:** ``expression``

    .. tagscript::

        {delete}
        {del(true==true)}
    """

    ACCEPTED_NAMES = ("delete", "del")

    def process(self, ctx: Context) -> Optional[str]:
        """
        Process the delete block
        """
        if "delete" in ctx.response.actions.keys():
            return ""
        if ctx.verb.parameter is None:
            value = True
        else:
            value = helper_parse_if(ctx.verb.parameter)
        ctx.response.actions["delete"] = value
        return ""