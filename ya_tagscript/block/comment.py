"""
Comment Block copied from Leg3ndary's bTagScript, licensed under Creative
Commons Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/Leg3ndary/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/comment_block.py
"""

from typing import Optional

from ..interface import Block
from ..interpreter import Context


class CommentBlock(Block):
    """
    The comment block is literally just for comments, it will not be
    parsed, however it will be removed from your codes output.

    **Usage:** ``{comment([other]):[text]}``

    **Aliases:** /, //, comment

    **Payload:** ``text``

    **Parameter:** ``other``

    .. tagscript::

        {//:My Comment!}

        {comment(Something):My Comment!}
    """

    ACCEPTED_NAMES = ("/", "//", "comment")

    def process(self, ctx: Context) -> Optional[str]:
        """
        Remove the block
        """
        return ""
