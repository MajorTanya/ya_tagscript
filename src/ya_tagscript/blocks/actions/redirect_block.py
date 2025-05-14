from ...interfaces import BlockABC
from ...interpreter import Context


class RedirectBlock(BlockABC):
    """
    Redirect the script output to a given channel, to the invoking user's DMs, or set
    it to be a reply to the invoking message.

    If it is used more than once in a script, only the latest redirection target will
    be retained.


    **Usage**: ``{redirect(<"dm"|"reply"|channel>)}``

    **Aliases**: ``redirect``

    **Parameter**: One of ``"dm"``, ``"reply"``, or ``channel`` (required)

    **Payload**: ``None``

    ``channel`` represents a way to refer to a text channel (e.g. channel name, mention
    string, ID, etc).

    Note:
        To avoid breaking scripts due to changing channel names, it is generally
        recommended to use channel IDs or mention strings to reference channels.

    **Examples**::

        {redirect(dm)}
        # Signals to redirect the output to the user's DMs

        {redirect(reply)}
        # Signals that the output should be a reply to the invoking message

        {redirect(#general)}
        # Signals to redirect the output to the #general channel

        {redirect(123)}
        # Signals to redirect the output to the channel with the ID 123

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["target"]``: :class:`Literal["dm", "reply"]` | :class:`str` — A
          string indicating the redirection target

    Note:
        This block will only set the ``target``
        :attr:`~ya_tagscript.interpreter.Response.actions` key as shown above. It is
        *up to the client* to implement actual redirection behaviour, including what
        constitutes a valid ``channel`` input (a client may choose to only accept IDs
        and reject channel names, for example).
    """

    requires_nonempty_parameter = False

    @property
    def _accepted_names(self) -> set[str]:
        return {"redirect"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None or param.strip() == "":
            return None

        parsed_param = ctx.interpret_segment(param).strip()

        if (lowered := parsed_param.lower()) == "dm":
            target = "dm"
        elif lowered == "reply":
            target = "reply"
        else:
            target = parsed_param
        ctx.response.actions["target"] = target
        return ""
