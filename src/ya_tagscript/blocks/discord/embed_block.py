import json
from collections.abc import Callable
from datetime import UTC, datetime
from inspect import ismethod
from typing import Any

from dateutil.parser import ParserError, parse
from discord import Colour, Embed

from ...exceptions import BadColourArgument, EmbedParseError
from ...interfaces import BlockABC
from ...interpreter import Context
from ...util import split_at_substring_zero_depth


def _add_field(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        raise EmbedParseError("`add_field` missing payload.")
    if len(embed.fields) == 25:
        raise EmbedParseError("Maximum number of embed fields exceeded (25).")
    data = split_at_substring_zero_depth(payload, "|", max_split=2)
    inline: bool | None = None
    if len(data) == 1:
        raise EmbedParseError("`add_field` payload was not split by |.")
    elif len(data) == 2:
        name = ctx.interpret_segment(data[0])
        payload = ctx.interpret_segment(data[1])
        inline = False
    elif len(data) == 3:
        name = ctx.interpret_segment(data[0])
        payload = ctx.interpret_segment(data[1])
        parsed_inline = ctx.interpret_segment(data[2])
        inline = (
            True
            if parsed_inline.lower() == "true"
            else False if parsed_inline.lower() == "false" else None
        )
    else:  # pragma: no cover
        # impossible due to max split of 2 meaning: 1 <= len(data) <= 3
        # but better to have this than to want for it
        raise EmbedParseError("`add_field` payload invalid.")
    if inline is None:
        raise EmbedParseError(
            f"`inline` argument for `add_field` is not a boolean value "
            f"(was `{data[2]}`).",
        )
    embed.add_field(name=name, value=payload, inline=inline)


def _set_author(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return
    data = split_at_substring_zero_depth(payload, "|", max_split=2)
    if len(data) == 1:
        parsed_name = ctx.interpret_segment(data[0])
        if parsed_name == "":
            return
        embed.set_author(name=parsed_name)
    elif len(data) == 2:
        parsed_name = ctx.interpret_segment(data[0])
        parsed_url = ctx.interpret_segment(data[1])
        if parsed_name == "":
            return
        embed.set_author(
            name=parsed_name,
            url=parsed_url if parsed_url != "" else None,
        )
    elif len(data) == 3:
        parsed_name = ctx.interpret_segment(data[0])
        parsed_url = ctx.interpret_segment(data[1])
        parsed_icon_url = ctx.interpret_segment(data[2])
        if parsed_name == "":
            return
        embed.set_author(
            name=parsed_name,
            url=parsed_url if parsed_url != "" else None,
            icon_url=parsed_icon_url if parsed_icon_url != "" else None,
        )
    else:  # pragma: no cover
        # impossible due to max split of 2 meaning: 1 <= len(data) <= 3
        raise EmbedParseError("`author` payload invalid.")


def _set_colour(
    ctx: Context,
    embed: Embed,
    attribute: str,
    payload: str | None,
) -> None:
    if payload is None:
        return
    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return

    colour = _string_to_colour(parsed_payload)
    setattr(embed, attribute, colour)


def _set_description(
    ctx: Context,
    embed: Embed,
    _: str,
    payload: str | None,
) -> None:
    if payload is None:
        return

    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return
    embed.description = parsed_payload


def _set_image_url(
    ctx: Context,
    embed: Embed,
    attribute: str,
    payload: str | None,
) -> None:
    if payload is None:
        return

    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return

    method = getattr(embed, f"set_{attribute}")
    method(url=parsed_payload)


def _set_footer(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return
    data = split_at_substring_zero_depth(payload, "|", max_split=1)
    if len(data) == 1:
        text = ctx.interpret_segment(data[0])
        embed.set_footer(text=text if text != "" else None)
    elif len(data) == 2:
        text = ctx.interpret_segment(data[0])
        icon_url = ctx.interpret_segment(data[1])
        embed.set_footer(
            text=text if text != "" else None,
            icon_url=icon_url if icon_url != "" else None,
        )
    else:  # pragma: no cover
        # impossible due to max split of 1 meaning: 1 <= len(data) <= 2
        raise EmbedParseError("`footer` payload invalid.")


def _set_timestamp(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return

    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return

    if parsed_payload.isdigit():
        ts = datetime.fromtimestamp(int(parsed_payload), tz=UTC)
    else:
        try:
            ts = parse(parsed_payload)
        except (ParserError, OverflowError):
            return
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    embed.timestamp = ts


def _set_title(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return

    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return

    embed.title = parsed_payload


def _set_url(ctx: Context, embed: Embed, _: str, payload: str | None) -> None:
    if payload is None:
        return

    parsed_payload = ctx.interpret_segment(payload)
    if parsed_payload == "":
        return

    embed.url = parsed_payload


def _string_to_colour(arg: str) -> Colour:
    arg = arg.replace("0x", "").lower()

    if arg[0] == "#":
        arg = arg.removeprefix("#")
    try:
        value = int(arg, base=16)
        if not (0 <= value <= 0xFFFFFF):
            raise BadColourArgument(arg)
        return Colour(value)
    except ValueError:
        arg = arg.replace(" ", "_")
        method = getattr(Colour, arg, None)
        if arg.startswith("from_") or method is None or not ismethod(method):
            raise BadColourArgument(arg)
        return method()


def _value_to_colour(value: Any) -> Colour | None:
    if value is None or isinstance(value, Colour):
        return value
    elif isinstance(value, int):
        return Colour(value)
    elif isinstance(value, str):
        return _string_to_colour(value)
    else:
        raise EmbedParseError(
            f"Received invalid type for colour key (expected Colour | str | int"
            f" | None, got {type(value).__qualname__}).",
        )


def _return_embed(ctx: Context, embed: Embed) -> str:
    try:
        size = len(embed)
    except KeyError as e:
        return str(e)
    if size > 6000:
        return f"`MAX EMBED LENGTH REACHED ({size}/6000)`"
    ctx.response.actions["embed"] = embed
    return ""


def _json_to_embed(text: str) -> Embed:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise EmbedParseError(e) from e

    if data.get("embed"):
        data = data["embed"]
    if data.get("timestamp"):
        data["timestamp"] = data["timestamp"].removesuffix("Z")

    colour = data.pop("colour", data.pop("color", None))

    embed = Embed.from_dict(data)

    if (colour := _value_to_colour(colour)) is not None:
        embed.colour = colour
    return embed


class EmbedBlock(BlockABC):
    """
    This block includes an embed in the tag response.

    There are two ways to use the embed block: manually inputting the accepted embed
    attributes or using properly formatted embed JSON from an embed generator.

    The JSON method allows complete embed customization (including setting attributes
    not supported by the manual method here), while the manual method provides
    control over individual attributes without requiring the entire block to be
    defined at once.

    **Manual**:

    The following embed attributes can be set manually:

    - ``author`` (see notes below)
    - ``title``
    - ``description``
    - ``color``
    - ``url``
    - ``thumbnail``
    - ``image``
    - ``footer`` (see notes below)
    - ``field`` (see notes below)
    - ``timestamp``

    Note:
        Some attributes expect a specially formed payload, these are explained below:

        - ``author``: The payload must be 1, 2, or 3 parts in size, with parts split by
          ``|``. The name is required, the other attributes are optional. If a name and
          an icon should be used *without* providing a website URL, leave the website
          URL empty but keep the ``|`` on either side.

          Valid ``author`` formats::

            {embed(author):name}
            {embed(author):name|website url}
            {embed(author):name|website url|icon url}
            # Note how the website url is left empty but the | are kept on either side
            {embed(author):name||icon url}

        - ``footer``: The payload must be 1 or 2 parts in size, with parts split by
          ``|``. The text is required, the icon URL is optional.

          Valid ``footer`` formats::

            {embed(footer):text}
            {embed(footer):text|icon URL}

        - ``field``: The payload must be 2 or 3 parts in size, with parts split by
          ``|``. The name and value are required, the inline status is optional. If
          inline is not set explicitly, it defaults to :data:`False`.

          Valid ``field`` formats::

            {embed(field):name|value}
            {embed(field):name|value|true}
            {embed(field):name|value|false}

    .. versionchanged:: 1.5
        The specially formed attributes (``author``, ``footer``, ``field``) now have a
        ":term:`zero-depth`" requirement for the ``|`` separating their attributes (see
        below).

    .. caution::
        With the introduction of :term:`zero-depth` restrictions on the `EmbedBlock` in
        v1.5.0, nested payloads are no longer supported. Because both ``author`` and
        ``footer`` have valid formats which don't require ``|`` at all (i.e. just
        ``name`` for ``author`` or just ``text`` for ``footer``), they will treat any
        payload without ``|`` at zero-depth as data for their ``name`` or ``text``
        attribute **only**.

        Incorrect example::

            {assign(author_payload):some name|https://website.example}
            {assign(footer_payload):some text|https://website.example/icon.png}
            {embed(author):{author_payload}}
            {embed(footer):{footer_payload}}

        This would result in the following Embed attributes:

        - ``embed.author.name``: ``"some name|https://website.example"``
        - ``embed.author.url``: :data:`None`
        - ``embed.author.icon_url``: :data:`None` (expected)
        - ``embed.footer.text``: ``"some text|https://website.example/icon.png"``
        - ``embed.footer.icon_url``: :data:`None`

        The correct thing to do is this::

            {embed(author):some name|https://website.example}
            {embed(footer):some text|https://website.example/icon.png}

        This would result in the following correct Embed attributes:

        - ``embed.author.name``: ``"some name"``
        - ``embed.author.url``: ``"https://website.example"``
        - ``embed.author.icon_url``: :data:`None` (expected)
        - ``embed.footer.text``: ``"some text"``
        - ``embed.footer.icon_url``: ``"https://website.example/icon.png"``


    **Usage**: ``{embed(<attribute>):<value>}``

    **Aliases**: ``embed``

    **Parameter**: ``attribute`` (required)

    **Payload**: ``value`` (required)

    **Examples**::

        {embed(color):#37b2cb}
        {embed(title):Rules}
        {embed(description):Follow these rules to ensure a good experience in our server!}
        {embed(field):Rule 1|Respect everyone you speak to.|false}
        {embed(footer):Thanks for reading!|{guild(icon)}}
        {embed(timestamp):1681234567}

    ----

    **JSON**:

    **Usage**: ``{embed(<json>)}``

    **Aliases**: ``embed``

    **Parameter**: ``json`` (required)

    **Payload**: ``None`` (ignored if JSON is used)

    **Examples**::

        # Note how the JSON sits entirely within the block's parameter section, even
        # when split across several lines.
        {embed({"title":"Hello!", "description":"This is a test embed."})}
        {embed({
            "title":"Here's a random duck!",
            "image":{"url":"https://random-d.uk/api/randomimg"},
            "color":15194415
        })}

    Both methods can be combined to create an embed in a tag. For example, JSON
    can be used to create an embed with fields, and the embed title can be set
    later.

    **Examples**::

        {embed({"fields":[{"name":"Field 1","value":"field description","inline":false}]})}
        {embed(title):my embed title}

    **Response Attribute**:

    This block sets the following attribute on the
    :class:`~ya_tagscript.interpreter.Response` object:

    - :attr:`~ya_tagscript.interpreter.Response.actions`
        - ``actions["embed"]``: :class:`discord.Embed` — The constructed
          :class:`discord.Embed`

    Note:
        This block only sets the ``embed`` actions key as shown above. It is *up to the
        client* to actually send the :class:`discord.Embed` object being constructed.
    """

    ATTRIBUTE_HANDLERS: dict[str, Callable[[Context, Embed, str, str | None], None]] = {
        "author": _set_author,
        "description": _set_description,
        "title": _set_title,
        "color": _set_colour,
        "colour": _set_colour,
        "url": _set_url,
        "thumbnail": _set_image_url,
        "image": _set_image_url,
        "field": _add_field,
        "footer": _set_footer,
        "timestamp": _set_timestamp,
    }

    @property
    def _accepted_names(self) -> set[str]:
        return {"embed"}

    def process(self, ctx: Context) -> str | None:
        if (param := ctx.node.parameter) is None:
            return _return_embed(ctx, ctx.response.actions.get("embed", Embed()))

        parsed_param = ctx.interpret_segment(param)
        lowercase_param = parsed_param.lower()
        try:
            if lowercase_param.startswith("{") and lowercase_param.endswith("}"):
                embed = _json_to_embed(parsed_param)
            elif lowercase_param in self.ATTRIBUTE_HANDLERS:
                embed = ctx.response.actions.get("embed", Embed())
                embed = self._update_embed(
                    ctx,
                    embed,
                    lowercase_param,
                    ctx.node.payload,
                )
            else:
                return None
        except EmbedParseError as e:
            return f"Embed Parse Error: {e}"

        return _return_embed(ctx, embed)

    @classmethod
    def _update_embed(
        cls,
        ctx: Context,
        embed: Embed,
        attribute: str,
        payload: str | None,
    ) -> Embed:
        handler = cls.ATTRIBUTE_HANDLERS[attribute]
        try:
            handler(ctx, embed, attribute, payload)
        except Exception as e:
            raise EmbedParseError(e) from e
        return embed
