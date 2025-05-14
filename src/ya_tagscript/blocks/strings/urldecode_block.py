from urllib.parse import unquote, unquote_plus

from ...interfaces import BlockABC
from ...interpreter import Context


class URLDecodeBlock(BlockABC):
    """
    This block decodes a URL-encoded string back into its original format.

    The payload is the URL-encoded string to be decoded.

    The parameter determines the decoding style: if the parameter is ``+``, *both*
    ``%20`` and ``+`` are decoded as a space; otherwise, *only* ``%20`` is decoded as
    a space. Other character sequences are decoded as normal in either case.

    **Usage**: ``{urldecode(<parameter>):<text>}``

    **Aliases**: ``urldecode``

    **Parameter**: ``+`` (optional) (all other values are ignored)

    **Payload**: ``text`` (required)

    **Examples**::

        {urldecode:hello%20world}
        # hello world

        {urldecode(+):Hello+there.+General+Kenobi.}
        # Hello there. General Kenobi.

        {urldecode(+):this%20is+a%20combined+test}
        # this is a combined test

        {urldecode:this+will+keep+the+plus+signs}
        # this+will+keep+the+plus+signs
    """

    requires_any_payload = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"urldecode"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None:
            return None

        parsed_payload = ctx.interpret_segment(payload)
        parsed_parameter = ctx.interpret_segment(ctx.node.parameter or "")

        encoder = unquote_plus if parsed_parameter == "+" else unquote
        return encoder(parsed_payload)
