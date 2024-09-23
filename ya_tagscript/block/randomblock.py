"""
Weighting logic copied from Leg3ndary's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/Leg3ndary/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/random_block.py
"""

import random
from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class RandomBlock(verb_required_block(True, payload=True)):
    """
    Picks a random item from a list of strings, split by either ``~`` or ``,``.
    An optional seed can be provided to the parameter to always choose the same item
    when using that seed.
    Items can be weighted differently by adding a weight and | before the item(s).

    **Usage:** ``{random([seed]):<list>}``

    **Aliases:** ``#, rand``

    **Payload:** list

    **Parameter:** seed, None

    **Examples:** ::

        {random:Carl,Harold,Josh} attempts to pick the lock!
        # Possible Outputs:
        # Josh attempts to pick the lock!
        # Carl attempts to pick the lock!
        # Harold attempts to pick the lock!

        {=(insults):You're so ugly that you went to the salon, and it took 3 hours just to get an estimate.~I'll never forget the first time we met, although I'll keep trying.~You look like a before picture.}
        {=(insult):{#:{insults}}}
        {insult}
        # Assigns a random insult to the insult variable

        {random:5|Cool,3|Lame}
        # 5 to 3 chances of "Cool" vs "Lame"
    """

    ACCEPTED_NAMES = ("random", "#", "rand")

    def process(self, ctx: Context) -> Optional[str]:
        if "~" in ctx.verb.payload:
            spl = ctx.verb.payload.split("~")
        else:
            spl = ctx.verb.payload.split(",")

        weights = []
        choices = []
        for choice in spl:
            if "|" in choice:
                weight, choice = choice.split("|", 1)
                weights.append(int(weight))
                choices.append(choice)
            else:
                weights.append(1)
                choices.append(choice)
        random.seed(ctx.verb.parameter)
        return random.choices(choices, weights, k=1)[0]
