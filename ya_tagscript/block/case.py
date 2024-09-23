"""
Case Block closely based on the UpperBlock and LowerBlock from Leg3ndary's bTagScript,
licensed under Creative Commons Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/Leg3ndary/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/case_block.py
"""

from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class CaseBlock(verb_required_block(True, payload=True)):
    """
    The Case Block, depending on the alias used, UPPERCASE or lowercase the payload.
    Without a payload, this block does nothing.

    **Usage:** ``{upper:<string>}`` OR ``{lower:<string>}``

    **Aliases:** ``upper``, ``lower``

    **Payload:** ``string``

    **Parameters:** ``None``

    **Examples:**

    .. tagscript::

        {upper:I am talking.}
        # I AM TALKING.

        {lower:I AM SCREAMING!}
        # i am screaming!
    """

    ACCEPTED_NAMES = ("upper", "lower")

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.declaration.lower() == "upper":
            return ctx.verb.payload.upper()
        elif ctx.verb.declaration.lower() == "lower":
            return ctx.verb.payload.lower()
        else:  # should be impossible with ACCEPTED_NAMES like this
            return None
