import random

from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class RandomBlock(BlockABC):
    """
    This block picks a random item from a list split by commas (``,``) or tildes
    (``~``).

    The separators must be consistent (only commas or only tildes).

    Note:
        The payload is interpreted *before* splitting at the separator, so this block
        *does not* have a ":term:`zero-depth`" requirement.

    An optional seed can be provided as the parameter to always choose the same item
    when using that seed.

    Items can be weighted differently by adding a weight and ``|`` to the item(s). Not
    all items need to be weighted. If no weight is provided, the item will be handled
    as if its weight was 1.

    **Usage**: ``{random([seed]):<list>}``

    **Aliases**: ``random``, ``rand``, ``#``

    **Parameter**: ``seed`` (optional)

    **Payload**: ``list`` (required)

    **Examples**::

        {random:Carl,Harold,Josh} attempts to pick the lock!
        # Possible Outputs:
        # Josh attempts to pick the lock!
        # Carl attempts to pick the lock!
        # Harold attempts to pick the lock!

        {random:5|Cool,3|Lame}
        # 5 to 3 odds of "Cool" vs "Lame"

        {random:first,10|second,third,4|fourth}
        # 10:4:1:1 odds of "second" vs "fourth" vs "first" vs "third"

        {assign(items):hello~hi~good morning}
        {assign(seed):123}
        {random({seed}):{items}}
        # 5:1:1 odds for "good morning" vs "hello" vs "hi"
        # but because the is seeded with "123": (Output below line)
        # ---
        # good morning
    """

    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"random", "rand", "#"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        if (param := ctx.node.parameter) is not None:
            seed = ctx.interpret_segment(param)
            _random = random.Random(seed)
        else:
            _random = random.Random()

        parsed_payload = ctx.interpret_segment(payload)
        if "~" in parsed_payload:
            split_payload = parsed_payload.split("~")
        else:
            split_payload = parsed_payload.split(",")

        # Weighting logic adapted from benz206's bTagScript, licensed under Creative
        # Commons Attribution 4.0 International License (CC BY 4.0).
        # cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/random_block.py
        items = []
        weights = []
        if any("|" in s_p for s_p in split_payload):
            # Weighted list of shape [weight|item, weight|item, ...]
            for item in split_payload:
                parts = split_at_substring_zero_depth(item, "|", max_split=1)
                weight = int(parts[0]) if len(parts) == 2 else 1
                items.append(parts[-1])
                weights.append(weight)
        else:
            items = split_payload
            weights = [1 for _ in split_payload]
        chosen = _random.choices(items, weights=weights, k=1)[0]
        parsed_chosen = ctx.interpret_segment(chosen)
        return parsed_chosen
