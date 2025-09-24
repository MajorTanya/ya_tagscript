"""
Comment Block adapted from benz206's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/comment_block.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context


class CommentBlock(BlockABC):
    """
    This block can be used to add comments in the script that are ignored during
    processing and removed from the output.

    Caution:
        *Everything* inside this block is ignored, *including nested blocks*.

    **Usage**: ``{comment([parameter]):[text]}``

    **Aliases**: ``/``, ``//``, ``comment``

    **Parameter**: ``parameter`` (ignored)

    **Payload**: ``text`` (ignored)

    **Examples**::

        {comment:My Comment!}
        # outputs nothing

        {comment(Something):My Comment!}
        # outputs nothing

        {comment:{cmd:echo hello world}}{cmd:ping}
        # outputs nothing and the "echo" command block will NOT be triggered BUT the
        # "ping" command WILL be set correctly because it is not nested inside the
        # comment block
    """

    @property
    def _accepted_names(self) -> set[str]:
        return {"/", "//", "comment"}

    def process(self, ctx: Context) -> str:
        return ""
