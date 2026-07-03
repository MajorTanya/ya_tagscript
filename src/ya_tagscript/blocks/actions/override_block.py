from ya_tagscript.interfaces import BlockABC
from ya_tagscript.interpreter import Context


class OverrideBlock(BlockABC):
    """
    Override a command's permission requirements.

    This block can override the permission requirements attached to a CommandBlock.

    Possible overrides are:
        - "admin": admin permissions
        - "mod": mod permissions
        - "permissions": general user permissions

    **Usage**: ``{override(["admin"|"mod"|"permissions"])}``

    **Aliases**: ``override``

    **Parameter**: One of ``admin``, ``mod``, ``permissions`` (optional)

    **Payload**: ``None``

    **Examples**::

        {override}
        # overrides all commands and permissions

        {override(admin)}
        # overrides commands that require the admin role

        {override(permissions)}
        {override(mod)}
        # overrides commands that require the mod role or have user permission requirements

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["overrides"]``:
          :class:`dict[Literal["admin", "mod", "permissions"], bool]` — A dictionary
          like ``{"admin": bool, "mod": bool, "permissions": bool}`` where each
          attribute is either :data:`True` or :data:`False`
        - The key is available via the
          :attr:`OverrideBlock.ACTIONS_KEY
          <ya_tagscript.blocks.OverrideBlock.ACTIONS_KEY>` class attribute

    Note:
        This block only sets the ``overrides``
        :attr:`~ya_tagscript.interpreter.Response.actions` key as shown above,
        combining the provided parameters across the entire script. It is *up to the
        client* to implement actual permission override behaviour as desired, including
        what permissions qualify for "admin", "mod", or "permissions".
    """

    ACTIONS_KEY = "overrides"
    """
    The key used to store data in the
    :attr:`Response.actions <ya_tagscript.interpreter.Response.actions>`.

    .. versionadded:: 1.7.1
    """

    _VALID_NAMES = {"override"}

    def process(self, ctx: Context) -> str | None:
        param = ctx.node.parameter
        if param is None:
            ctx.response.actions[OverrideBlock.ACTIONS_KEY] = {
                "admin": True,
                "mod": True,
                "permissions": True,
            }
            return ""

        parsed_param = ctx.interpret_segment(param)
        if parsed_param not in ("admin", "mod", "permissions"):
            return None

        overrides = ctx.response.actions.get(
            OverrideBlock.ACTIONS_KEY,
            {"admin": False, "mod": False, "permissions": False},
        )
        overrides[parsed_param] = True
        ctx.response.actions[OverrideBlock.ACTIONS_KEY] = overrides
        return ""
