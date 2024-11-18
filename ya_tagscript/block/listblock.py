from typing import Optional

from ..interface import verb_required_block
from ..interpreter import Context


class ListBlock(verb_required_block(True, payload=True, parameter=True)):
    """
    The List Block retrieves the element from the payload at the index specified by the
    parameter.

    Both variants are 0-indexed and allow for backwards parsing using negative values.
    If the parameter is not a number, both blocks will return an error.

    ``list`` returns the element in the payload that corresponds to the given index
    (passed as the parameter) or an empty string if the index is out of bounds. Splits
    on tilde (~).

    ``cycle`` returns the element in the payload that corresponds to the given index
    (passed as the parameter). It will loop around to the beginning of the payload if
    the index becomes out of bounds (index = index % len(payload)). Splits on tilde (~).

    **Usage:** ``{list(<number>):<payload>}``

    **Aliases:** ``cycle``

    **Payload:** payload

    **Parameter:** number

    **Examples:** ::

        {list(1):apple~banana~secret third thing}
        # banana
        {list(-2):apple~banana~secret third thing}
        # apple
        {list(10):apple~banana~secret third thing}
        # (causes an error)

        {cycle(1):apple~banana~secret third thing}
        # banana
        {cycle(-2):apple~banana~secret third thing}
        # apple
        {cycle(10):apple~banana~secret third thing}
        # banana
    """

    ACCEPTED_NAMES = ("list", "cycle")

    def process(self, ctx: Context) -> Optional[str]:
        dec = ctx.verb.declaration.lower()
        try:
            index = int(ctx.verb.parameter)
        except ValueError:
            return f"Could not parse {ctx.verb.declaration.lower()} index"
        haystack = ctx.verb.payload.split("~")
        if dec == "list":
            return "" if (len(haystack) - 1) < index else haystack[index]
        elif dec == "cycle":
            return haystack[index % len(haystack)]
