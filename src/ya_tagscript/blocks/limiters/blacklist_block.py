from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class BlacklistBlock(BlockABC):
    """
    Signals to blacklist specific channels or roles, preventing the tag from being used
    in the specified channels or by users with the specified roles.

    If an invocation should be blocked, the optional response payload can be sent.

    Note:
        The blacklist items can be any strings, regardless of their validity as channel
        or role identifiers. It is up the client to validate the list of blacklisted
        items.

    This block does not interrupt the interpretation of the tag; subsequent blocks are
    still executed, and the response output continues to be built.

    **Usage**: ``{blacklist(<blocked>):[response]}``

    **Aliases**: ``blacklist``

    **Parameter**: ``blocked`` (required)

    **Payload**: ``response`` (optional)

    **Examples**::

        {blacklist(Muted)}
        # Blacklists the "Muted" channel or  role

        {blacklist(#support):This tag is not allowed in #support.}
        # Blacklists the #support channel or role with a custom response message

        {blacklist(Tag Blacklist, 668713062186090506):You are blacklisted from using tags.}
        # Blacklists multiple roles or channels with a custom response message

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["blacklist"]``: :class:`dict[Literal["items", "response"],
          list[str] | str | None]` — A dictionary like
          ``{"items": [...], "response": "..."}``

          - ``"items"``: A list of strings representing channels or roles
          - ``"response"``: A response :class:`str` OR :data:`None` if no ``response``
            was provided to the block

    Note:
        This block only adds the blacklist information in the ``blacklist`` actions
        key as shown above. It is the *responsibility of the client* to implement the
        actual blacklist blocking system. It is also the *client's responsibility* to
        prevent side effects like commands, reactions, etc. from being executed if the
        tag execution is blacklisted somehow.
    """

    requires_nonempty_parameter = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"blacklist"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None
        elif ctx.response.actions.get("blacklist") is not None:
            return None

        parsed_param = ctx.interpret_segment(param)
        split = split_at_substring_zero_depth(parsed_param, ",")

        response = None
        if ctx.node.payload is not None:
            response = ctx.interpret_segment(ctx.node.payload)
        ctx.response.actions["blacklist"] = {
            "items": [b.strip() for b in split],
            "response": response,
        }
        return ""
