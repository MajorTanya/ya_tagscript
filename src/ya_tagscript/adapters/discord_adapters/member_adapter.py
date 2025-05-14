import discord

from .attribute_adapter import AttributeAdapter


class MemberAdapter(AttributeAdapter):
    """A :class:`discord.Member` adapter

    **Attributes**:

    (from base :class:`AttributeAdapter`)

    - ``id``: :class:`int` — The user's ID
    - ``created_at``: :class:`~datetime.datetime` — Represents the user's creation time
    - ``timestamp``: :class:`int` — The seconds-based timestamp of the user's
      ``created_at`` attribute
    - ``name``: :class:`str` — The user's name

    (:class:`discord.Member`-specific)

    - ``color`` :class:`discord.Colour` — The colour the user's name is shown in
      (depends on their top role) (alias: ``colour``)
    - ``colour`` :class:`discord.Colour` — The colour the user's name is shown in
      (depends on their top role) (alias: ``color``)
    - ``global_name``: :class:`str` | :data:`None` — The user's global nickname
    - ``nick``: :class:`str` | :data:`None` — The user's guild-specific nickname
    - ``avatar`` :class:`tuple[str, Literal[False]]` — The user's avatar. The first
      tuple element contains the avatar's URL. The False instructs the adapter to not
      escape the contents of this attribute.
    - ``discriminator``: :class:`str` — The user's discriminator
    - ``joined_at``: :class:`~datetime.datetime` — The user's time of joining this
      guild. If the user has left the guild, this falls back to the user's creation
      time.
    - ``joinstamp``: :class:`int` — The seconds-based timestamp of the user's
      joined_at attribute
    - ``mention``: :class:`str` — The mention string for this user
    - ``bot``: :class:`bool` — Whether this user is a bot account
    - ``top_role``: :class:`discord.Role` — The user's topmost role
    - ``roleids``: :class:`str` — A space-separated list of the IDs of each role of
      this user.
    """

    def __init__(self, member: discord.Member):
        super().__init__(base=member)
        joined_at = member.joined_at or member.created_at
        additional_attributes = {
            "color": member.color,
            "colour": member.colour,
            "global_name": member.global_name,
            "nick": member.nick,
            "avatar": (member.display_avatar.url, False),
            "discriminator": member.discriminator,
            "joined_at": joined_at,
            "joinstamp": int(joined_at.timestamp()),
            "mention": member.mention,
            "bot": member.bot,
            "top_role": member.top_role,
            "roleids": " ".join(str(rid.id) for rid in member.roles),
        }
        self._attributes.update(additional_attributes)
