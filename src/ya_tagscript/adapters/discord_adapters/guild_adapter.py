import random
from collections.abc import Sequence

import discord

from .attribute_adapter import AttributeAdapter


class GuildAdapter(AttributeAdapter):
    """A :class:`discord.Guild` adapter

    **Attributes**:

    (from base :class:`AttributeAdapter`)

    - ``id``: :class:`int` — The guild's ID
    - ``created_at``: :class:`~datetime.datetime` — Represents the guild's creation
      time
    - ``timestamp``: :class:`int` — The seconds-based timestamp of the guild's
      ``created_at`` attribute
    - ``name``: :class:`str` — The guild's name

    (:class:`discord.Guild`-specific)

    - ``icon``: :class:`tuple[str, Literal[False]]` — The guild's icon. The first tuple
      element contains the icon's URL or is empty. The :data:`False` instructs the
      adapter to not escape the contents of this attribute.
    - ``member_count``: :class:`int` | :data:`None` — The number of members in this
      guild (alias: ``members``) (Can be :data:`None` under some circumstances)
    - ``members``: :class:`int` | :data:`None` — The number of members in this guild
      (alias: ``member_count``) (Can be :class:`None` under some circumstances)
    - ``bots``: :class:`int` — The number of bots in this guild
    - ``humans``: :class:`int` — The number of human users in this guild
    - ``description``: :class:`str` — The guild's description

    - ``random``: :class:`discord.Member` — Returns a randomly chosen member of the
      guild
    """

    def __init__(self, guild: discord.Guild) -> None:
        super().__init__(base=guild)
        bots = 0
        humans = 0
        for m in guild.members:
            if m.bot:
                bots += 1
            else:
                humans += 1
        additional_attributes = {
            "icon": (getattr(guild.icon, "url", ""), False),
            "member_count": guild.member_count,
            "members": guild.member_count,
            "bots": bots,
            "humans": humans,
            "description": guild.description or "No description.",
        }
        self._attributes.update(additional_attributes)
        additional_methods = {"random": self.random_member}
        self._methods.update(additional_methods)

    def random_member(self) -> discord.Member:
        members: Sequence[discord.Member] = self.object.members
        return random.choice(members)
