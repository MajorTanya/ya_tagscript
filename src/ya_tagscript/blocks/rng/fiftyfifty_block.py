import random

from ...interfaces import BlockABC
from ...interpreter import Context


class FiftyFiftyBlock(BlockABC):
    """
    This block has a 50% change of returning the (interpreted) payload, and 50% chance
    of returning an empty string.

    **Usage**: ``{5050:<message>}``

    **Aliases**: ``5050``, ``50``, ``?``

    **Parameter**: ``None``

    **Payload**: ``message`` (required)

    **Examples**:  ::

        I pick {if({5050:.}!=):heads|tails}!
        # I pick heads! (50% chance)
    """

    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"5050", "50", "?"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None:
            return None

        return random.choice(["", ctx.interpret_segment(payload)])
