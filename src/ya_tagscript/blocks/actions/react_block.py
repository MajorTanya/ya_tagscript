"""
React Block adapted from benz206's bTagScript, licensed under Creative Commons
Attribution 4.0 International License (CC BY 4.0).

cf. https://github.com/benz206/bTagScript/blob/945b8e34750debea714d36de863412e189975c1b/bTagScript/block/discord_blocks/react_block.py
"""

from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


class ReactBlock(BlockABC):
    """
    Provide a list of reactions to be added to either the input message or the script
    output.

    By default, only 5 emoji can be specified for either the input or output message,
    for a total of 10 emoji (max. 5 for input + max. 5 for output).

    When providing several emoji, they have to be separated by a space.

    Behaviour differs between aliases:

    - ``react``: Emoji to add as reactions to the output message
    - ``reactu``: ("react-up") Emoji to add as reactions to the input message

    Note:
        The emoji can be any strings, regardless of their validity as standard emoji or
        Discord server emotes. It is *up to the client* to validate the provided list
        of emoji.

    If the same alias is used again in the script, the previous emoji are overwritten,
    so only the latest set of emoji is retained.

    **Usage**: ``{react:<emoji>}``

    **Aliases**: ``react``, ``reactu``

    **Parameter**: ``None``

    **Payload**: ``emoji`` (required)

    **Examples**::

        {react:💩}
        # 💩 is added to the list of reactions for the output message

        {react:💩 :)}
        # both "💩" and ":)" are added to the list of reactions for the output message

        {reactu:🤔 :) :D}
        # "🤔", ":)", and ":D" are added to the list of reactions for the input message

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["reactions"]``:
          :class:`dict[Literal["input", "output"], list[str]]` — A dictionary like
          ``{"input": [...], "output": [...]}`` (each key may be missing if it wasn't
          used in the script)

    Note:
        This block will only set the provided string(s) in the ``reactions``
        :attr:`~ya_tagscript.interpreter.Response.actions` key under the appropriate
        dictionary key as shown above. Each of the keys may be missing if not used in
        the script. It is *up to the client* to implement actual reaction adding
        behaviour as desired.
    """

    requires_nonempty_payload = True

    def __init__(self, limit: int = 5) -> None:
        self.limit = limit

    @property
    def _accepted_names(self) -> set[str]:
        return {"react", "reactu"}

    def process(self, ctx: Context) -> str | None:
        if (declaration := ctx.node.declaration) is None or declaration.strip() == "":
            return None
        elif (payload := ctx.node.payload) is None or payload.strip() == "":
            return None

        parsed_declaration = ctx.interpret_segment(declaration).lower()
        parsed_payload = ctx.interpret_segment(payload).strip()
        reactions = split_at_substring_zero_depth(parsed_payload, " ")
        # ignore empty strings (caused by more than one space between emoji)
        reactions = [r for r in reactions if r != ""]

        if len(reactions) > self.limit:
            return f"`Reaction Limit Reached ({self.limit})`"

        if parsed_declaration == "react":
            reactions_dict = ctx.response.actions.get("reactions", {})
            reactions_dict.update({"output": reactions})
            ctx.response.actions["reactions"] = reactions_dict
        elif parsed_declaration == "reactu":
            reactions_dict = ctx.response.actions.get("reactions", {})
            reactions_dict.update({"input": reactions})
            ctx.response.actions["reactions"] = reactions_dict
        else:
            return None
        return ""
