import random
import re

from ...interfaces import BlockABC
from ...interpreter import Context

_RANGE_PATTERN = re.compile(r"(?P<lower>-?\d+(?:\.\d+)?)-(?P<upper>-?\d+(?:\.\d+)?)")


class RangeBlock(BlockABC):
    """
    This block picks a random number from a range of numbers separated by ``-``.

    The number range is inclusive (i.e. ``[lowest, highest]``), so the bounding numbers
    can be returned as well. Both bounds can be negative.

    If the lower bound is larger than the upper bound, the block will return an error
    message.

    Behaviour differs between aliases:

    - ``range``: Returns integers (bounds are truncated to integers)
    - ``rangef``: Returns floating point numbers

    An optional seed can be provided as the parameter to always choose the same item
    when using that seed.

    **Usage**: ``{range([seed]):<lowest>-<highest>}``

    **Aliases**: ``range``, ``rangef``

    **Parameter**: ``seed`` (optional)

    **Payload**: ``lowest-highest`` (both are numbers) (required)

    **Examples**::

        Your lucky number is {range:10-30}!
        # Your lucky number is 14!

        {=(height):{rangef:5-7}}
        I am guessing your height is {height}ft.
        # I am guessing your height is 5.3ft.
    """

    _PRECISION = 1_000_000_000_000_000  # 1e15

    requires_nonempty_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"range", "rangef"}

    def process(self, ctx: Context) -> str | None:
        if ((declaration := ctx.node.declaration) is None) or (
            declaration not in self._accepted_names
        ):
            return None
        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        if (param := ctx.node.parameter) is not None:
            seed = ctx.interpret_segment(param)
            _random = random.Random(seed)
        else:
            _random = random.Random()

        parsed_payload = ctx.interpret_segment(payload)
        if (found := re.fullmatch(_RANGE_PATTERN, parsed_payload)) is None:
            return None
        elif len(found.groups()) != 2:  # pragma: no cover
            # this case should be impossible due to the two capturing groups in
            # _RANGE_PATTERN and the use of fullmatch on the payload
            return None

        lower_bound_str = found.group("lower")
        upper_bound_str = found.group("upper")

        result: int | float
        if declaration == "range":
            lower_bound = int(float(lower_bound_str))
            upper_bound = int(float(upper_bound_str))
            if lower_bound > upper_bound:
                return f"Lower {declaration} bound was larger than upper bound"
            result = _random.randint(lower_bound, upper_bound)
            return str(result)
        elif declaration == "rangef":
            lower_bound = int(float(lower_bound_str) * self._PRECISION)
            upper_bound = int(float(upper_bound_str) * self._PRECISION)
            if lower_bound > upper_bound:
                return f"Lower {declaration} bound was larger than upper bound"
            result = _random.randint(lower_bound, upper_bound) / self._PRECISION
            return str(result)

        # getting here is impossible due to the early guard on declaration
        return None  # pragma: no cover
