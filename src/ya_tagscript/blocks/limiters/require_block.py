from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class RequireBlock(BlockABC):
    """
    Signals to require specific channels or roles, ensuring the tag can only be used in
    the specified channels or by users with the specified roles or in the specified
    channels.

    If an invocation should be blocked, the optional response payload can be sent.

    Note:
        The required items can be any strings, regardless of their validity as channel
        or role identifiers. It is up the client to validate the list of required
        items.

    This block does not interrupt the interpretation of the tag; subsequent blocks
    are still executed, and the response output continues to be built. If the user
    does not meet the requirements, an optional response message can be sent.

    **Usage**: ``{require(<required>):[response]}``

    **Aliases**: ``require``, ``whitelist``

    **Parameter**: ``required`` (required)

    **Payload**: ``response`` (optional)

    **Examples**::

        {require(Moderator)}
        # Requires the "Moderator" channel or role

        {require(#general, #bot-cmds):This tag can only be run in #general and #bot-cmds.}
        # Requires the #general and #bot-cmds channels or roles with a custom response message

        {require(757425366209134764, 668713062186090506, 737961895356792882):You aren't allowed to use this tag.}
        # Requires the specified channel or role IDs with a custom response message

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["requires"]``: :class:`dict[Literal["items", "response"],
          list[str] | str | None]` — A dictionary like
          ``{"items": [...], "response": "..."}``

          - ``"items"``: A list of strings representing channels or roles
          - ``"response"``: A response :class:`str` OR :data:`None` if no ``response``
            was provided to the block

    Note:
        This block only adds the requirement information in the ``requires`` actions
        key as shown above. It is the *responsibility of the client* to implement the
        actual requirement enforcement system. It is also the *client's responsibility*
        to prevent side effects like commands, reactions, etc. from being executed if
        the tag execution does not meet the requirements and is therefore blocked.
    """

    requires_nonempty_parameter = True

    @property
    def _accepted_names(self) -> set[str]:
        return {"require", "whitelist"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None
        elif ctx.response.actions.get("requires") is not None:
            return None

        parsed_param = ctx.interpret_segment(param)
        split = split_at_substring_zero_depth(parsed_param, ",")

        response = None
        if ctx.node.payload is not None:
            response = ctx.interpret_segment(ctx.node.payload)
        ctx.response.actions["requires"] = {
            "items": [r.strip() for r in split],
            "response": response,
        }
        return ""
