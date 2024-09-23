"""
React Block copied from Leg3ndary's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/Leg3ndary/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/discord_blocks/react_block.py
"""

from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class ReactBlock(verb_required_block(True, payload=True)):
    """
    The React Block will set the actions "react" key to a list of reactions.

    .. note::

        You must set the behaviour manually.

    **Usage:** ``{react:<emojis>}``

    **Aliases:** ``None``

    **Payload:** ``emojis``

    **Parameter:** ``None``

    .. tagscript::

        {react:💩}
        {react:💩,:)}
        {react:💩~:)~:D}
    """

    ACCEPTED_NAMES = ("react",)

    def __init__(self, limit: int = 5) -> None:
        """
        Initialize the block

        Limit is the maximum number of reactions the block will add
        """
        self.limit = limit
        super().__init__()

    def process(self, ctx: Context) -> Optional[str]:
        """
        Process the reactions
        """
        reactions = ctx.verb.payload.strip().split(
            "~" if "~" in ctx.verb.payload else ","
        )
        if len(reactions) > self.limit:
            return f"`Reaction Limit Reached ({self.limit})"
        ctx.response.actions["reactions"] = reactions
        return ""
