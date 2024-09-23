import random
from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class FiftyFiftyBlock(verb_required_block(True, payload=True)):
    """
    The Fifty-Fifty Block has a 50% change of returning the payload, and 50% chance of
    returning an empty string.

    **Usage:**  ``{50:<message>}``

    **Aliases:**  ``5050, ?``

    **Payload:**  message

    **Parameter:**  None

    **Examples:**  ::

        I pick {if({5050:.}!=):heads|tails}
        # I pick heads
    """

    ACCEPTED_NAMES = ("5050", "50", "?")

    def process(self, ctx: Context) -> Optional[str]:
        return random.choice(["", ctx.verb.payload])
