from ...interfaces import BlockABC
from ...interpreter import Context


class CommandBlock(BlockABC):
    """
    Run a command as if the tag invoker had run it.

    By default, only 3 command blocks can be used in a tag.

    **Usage**: ``{command:<command text>}``

    **Aliases**: ``c``, ``com``, ``cmd``, ``command``

    **Parameter**: ``None``

    **Payload**: ``command text`` (required)

    **Examples**::

        {c:ping}
        # adds "ping" to the "commands" list of the Response's actions attribute

        {c:ban {target(id)} flooding/spam}
        # (Assuming target is a user with ID 123)
        # adds "ban 123 flooding/spam"

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["commands"]``: :class:`list[str]` | :data:`None` — A list of
          command strings or :data:`None`

    Note:
        This block will only add the processed command strings to the ``commands``
        :attr:`~ya_tagscript.interpreter.Response.actions` key as shown above. It is
        *up to the client* to implement actual command execution behaviour as desired.
    """

    requires_nonempty_payload = True

    def __init__(self, limit: int = 3) -> None:
        self.limit = limit

    @property
    def _accepted_names(self) -> set[str]:
        return {"c", "com", "cmd", "command"}

    def process(self, ctx: Context) -> str | None:
        if (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        command = ctx.interpret_segment(payload)

        commands: list[str] | None = ctx.response.actions.get("commands")
        if commands is not None:
            if len(commands) >= self.limit:
                return f"`COMMAND LIMIT REACHED ({self.limit})`"
            ctx.response.actions["commands"].append(command)
        else:
            ctx.response.actions["commands"] = [command]

        return ""
