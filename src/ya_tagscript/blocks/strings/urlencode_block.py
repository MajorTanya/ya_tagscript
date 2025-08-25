from urllib.parse import quote, quote_plus

from ...interfaces import BlockABC
from ...interpreter import Context


class URLEncodeBlock(BlockABC):
    """
    This block encodes a string into a URL-safe format.

    The payload is the string to be encoded.

    The parameter determines the encoding style: if the parameter is ``+``, spaces are
    encoded as ``+``; otherwise, spaces are encoded as ``%20``.

    **Usage**: ``{urlencode(<parameter>):<text>}``

    **Aliases**: ``urlencode``

    **Parameter**: ``+`` (optional) (all other values are ignored)

    **Payload**: ``text`` (required)

    **Examples**::

        {urlencode:covid-19 sucks}
        # covid-19%20sucks

        {urlencode(+):im stuck at home writing docs}
        # im+stuck+at+home+writing+docs

        # the following tagscript can be used to search up tag blocks
        # assume {args} = "command block"
        <https://ya-tagscript.readthedocs.io/en/latest/search.html?q={urlencode(+):{args}}&check_keywords=yes&area=default>
        # <https://ya-tagscript.readthedocs.io/en/latest/search.html?q=command+block&check_keywords=yes&area=default>
    """

    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"urlencode"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None:
            return None

        parsed_payload = ctx.interpret_segment(payload)
        parsed_parameter = ctx.interpret_segment(ctx.node.parameter or "")

        encoder = quote_plus if parsed_parameter == "+" else quote
        return encoder(parsed_payload)
