from typing import Any

import discord

from .attribute_adapter import AttributeAdapter


class ChannelAdapter(AttributeAdapter):
    """A :class:`discord.TextChannel` adapter

    Note:
        Only :class:`discord.TextChannel` instances are fully supported. The
        constructor accepts ``Any`` to avoid type checking issues when creating this
        adapter with the :attr:`discord.ext.commands.Context.channel` attribute, which
        could be any kind of channel. This loose typing allows the construction with
        that attribute but doesn't set any of the :class:`discord.TextChannel`-specific
        attributes.

    **Attributes**:

    (from base :class:`AttributeAdapter`)

    - ``id``: :class:`int` — The channel's ID
    - ``created_at``: :class:`~datetime.datetime` — Represents the channel's creation
      time
    - ``timestamp``: :class:`int` — The seconds-based timestamp of the channel's
      ``created_at`` attribute
    - ``name``: :class:`str` — The channel's name

    (:class:`discord.TextChannel`-specific)

    - ``nsfw``: :class:`bool` — Whether this :class:`discord.TextChannel` is marked as
      NSFW and is therefore age-gated
    - ``mention``: :class:`str` — The mention string for this channel
    - ``topic``: :class:`str` | :data:`None` — The channel's topic, if it exists and
      :data:`None` otherwise
    - ``slowmode``: :class:`int` — The slowmode delay of the channel in seconds
      (0 represents a disabled slowmode)
    - ``position``: :class:`int` — The position of the channel in the channel list
    """

    def __init__(self, channel: Any):
        # hard to type usefully since ctx.channel might not be TextChannel
        super().__init__(base=channel)
        if not isinstance(channel, discord.TextChannel):
            return
        additional_attributes = {
            "nsfw": channel.nsfw,
            "mention": channel.mention,
            "topic": channel.topic,
            "slowmode": channel.slowmode_delay,
            "position": channel.position,
        }
        self._attributes.update(additional_attributes)
