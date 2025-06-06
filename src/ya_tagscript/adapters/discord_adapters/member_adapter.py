import discord

from .attribute_adapter import AttributeAdapter


class MemberAdapter(AttributeAdapter):
    """A :class:`discord.Member` and :class:`discord.User` adapter

    **Attributes**:

    (from base :class:`AttributeAdapter`)

    - ``id``: :class:`int` — The user's ID
    - ``created_at``: :class:`~datetime.datetime` — Represents the user's creation time
    - ``timestamp``: :class:`int` — The seconds-based timestamp of the user's
      ``created_at`` attribute
    - ``name``: :class:`str` — The user's name

    (:class:`discord.Member` or :class:`discord.User`-specific)

    - ``color``: :class:`discord.Colour` — The colour the user's name is shown in
      (depends on their top role) (alias: ``colour``)
    - ``colour``: :class:`discord.Colour` — The colour the user's name is shown in
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

    Note:
        This adapter also supports :class:`discord.User` as a convenience matter. For
        example, the :attr:`~discord.ext.commands.Context.author` attribute of the
        :class:`discord.ext.commands.Context` could be a :class:`~discord.Member` or a
        :class:`~discord.User`, depending on whether the command was used in a guild or
        not.

        Some attributes that don't make sense on non-:class:`discord.Member` users fall
        back to sensible defaults:

            - ``joined_at`` falls back to the value of ``created_at``
            - ``nick`` falls back to the value of ``global_name``
            - ``top_role`` falls back to an empty string
            - ``roleids`` falls back to an empty string

    .. versionchanged:: 1.2
        Now supports passing a :class:`discord.User` as well, with fallback values as
        described above.
    """

    def __init__(self, member: discord.Member | discord.User):
        super().__init__(base=member)
        if isinstance(member, discord.Member):
            joined_at = member.joined_at or member.created_at
            nick = member.nick
            top_role = member.top_role
            roles = member.roles
        else:
            joined_at = member.created_at
            nick = member.global_name
            # cannot be None as that is interpreted as "block rejected" when returned
            # by the accessing variable getter block
            top_role = ""
            roles = []

        additional_attributes = {
            "color": member.color,
            "colour": member.colour,
            "global_name": member.global_name,
            "nick": nick,
            "avatar": (member.display_avatar.url, False),
            "discriminator": member.discriminator,
            "joined_at": joined_at,
            "joinstamp": int(joined_at.timestamp()),
            "mention": member.mention,
            "bot": member.bot,
            "top_role": top_role,
            "roleids": " ".join(str(rid.id) for rid in roles),
        }
        self._attributes.update(additional_attributes)
