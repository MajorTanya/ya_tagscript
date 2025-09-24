"""
Case Block adapted from the UpperBlock and LowerBlock from benz206's bTagScript,
licensed under Creative Commons Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/case_block.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context


class CaseBlock(BlockABC):
    """
    This block modifies the case of the provided payload.

    Behaviour differs between aliases:

    - ``lower``: Converts the payload to lowercase
    - ``upper``: Converts the payload to uppercase

    **Usage**: ``{lower:<text>}`` or ``{upper:<text>}``

    **Aliases**: ``lower``, ``upper``

    **Parameter**: ``None``

    **Payload**: ``text`` (required)

    **Examples**::

        {lower:SCREAMING!}
        # screaming!

        {upper:I am talking.}
        # I AM TALKING.
    """

    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"lower", "upper"}

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None:
            return None
        elif (payload := ctx.node.payload) is None or payload == "":
            return ""

        if declaration.lower() == "upper":
            return ctx.interpret_segment(payload).upper()
        elif declaration.lower() == "lower":
            return ctx.interpret_segment(payload).lower()

        return None
