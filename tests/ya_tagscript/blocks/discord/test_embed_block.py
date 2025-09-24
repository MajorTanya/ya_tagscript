import textwrap
from datetime import UTC, datetime
from unittest.mock import MagicMock

import discord
import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.EmbedBlock(),
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(b)


def test_accepted_names():
    block = blocks.EmbedBlock()
    assert block._accepted_names == {"embed"}


def test_process_method_accepts_missing_parameter():
    # this results in an empty Embed being instantiated internally
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None
    mock_ctx.response = MagicMock(spec=interpreter.Response)
    mock_ctx.response.actions = {}

    block = blocks.EmbedBlock()
    returned = block.process(mock_ctx)
    assert returned == ""
    embed = mock_ctx.response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed) == 0


def test_embed_len_key_error_raised_is_returned():
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_ctx.node = MagicMock(spec=interfaces.NodeABC)
    mock_ctx.node.parameter = None
    mock_embed = MagicMock(spec=discord.Embed)
    mock_embed.__len__.side_effect = KeyError("some key error")
    mock_ctx.response = MagicMock(spec=interpreter.Response)
    mock_ctx.response.actions = {"embed": mock_embed}

    block = blocks.EmbedBlock()
    assert block.process(mock_ctx) == "'some key error'"


def test_dec_embed_unknown_attributes_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(clown):test}"
    response = ts_interpreter.process(script)
    assert response.body == script


def test_dec_embed_parameter_is_interpreted_in_json(
    ts_interpreter: TagScriptInterpreter,
):
    script = '{embed({"title": "{my_var}"})}'
    data = {"my_var": adapters.StringAdapter("my title")}
    response = ts_interpreter.process(script, data)
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == "my title"


def test_dec_embed_parameter_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed({my_var}):my description}"
    data = {"my_var": adapters.StringAdapter("description")}
    response = ts_interpreter.process(script, data)
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.description == "my description"


def test_dec_embed_payload_is_interpreted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(title):This is {my_var}}"
    data = {"my_var": adapters.StringAdapter("Sparta!")}
    response = ts_interpreter.process(script, data)
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == "This is Sparta!"


def test_dec_embed_docs_example_one(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{embed(color):#37b2cb}"
        + "{embed(title):Rules}"
        + "{embed(description):Follow these rules to ensure a good experience in our server!}"
        + "{embed(field):Rule 1|Respect everyone you speak to.|false}"
        + "{embed(footer):Thanks for reading!|{guild(icon)}}"
        + "{embed(timestamp):1681234567}"
    )
    response = ts_interpreter.process(script)
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    assert embed.colour.value == int("37B2CB", base=16)
    assert embed.title == "Rules"
    assert (
        embed.description
        == "Follow these rules to ensure a good experience in our server!"
    )
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "Rule 1"
    assert embed.fields[0].value == "Respect everyone you speak to."
    assert embed.fields[0].inline == False
    assert isinstance(embed.timestamp, datetime)
    assert int(embed.timestamp.timestamp()) == 1681234567


def test_dec_embed_docs_example_two(
    ts_interpreter: TagScriptInterpreter,
):
    script = '{embed({"title": "Hello!", "description": "This is a test embed."})}'
    response = ts_interpreter.process(script)
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Hello!"
    assert embed.description == "This is a test embed."


def test_dec_embed_docs_example_three(
    ts_interpreter: TagScriptInterpreter,
):
    script = """{embed({
"title":"Here's a random duck!",
"image":{"url":"https://random-d.uk/api/randomimg"},
"color":15194415
})}"""
    response = ts_interpreter.process(script)
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.title == "Here's a random duck!"
    assert embed.image is not None
    assert embed.image.url == "https://random-d.uk/api/randomimg"
    assert embed.colour is not None
    assert embed.colour.value == 15194415


def test_dec_embed_docs_example_four(
    ts_interpreter: TagScriptInterpreter,
):
    script = '{embed({"fields":[{"name":"Field 1","value":"field description","inline":false}]})}{embed(title):my embed title}'
    response = ts_interpreter.process(script)
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "Field 1"
    assert embed.fields[0].value == "field description"
    assert embed.fields[0].inline == False
    assert embed.title == "my embed title"


def test_dec_embed_docs_v1_5_incorrect_example(
    ts_interpreter: TagScriptInterpreter,
):
    script = textwrap.dedent(
        """
        {assign(author_payload):some name|https://website.example}
        {assign(footer_payload):some text|https://website.example/icon.png}
        {embed(author):{author_payload}}
        {embed(footer):{footer_payload}}
        """,
    ).strip()
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "some name|https://website.example"
    assert embed.author.url is None
    assert embed.author.icon_url is None
    assert embed.footer.text == "some text|https://website.example/icon.png"
    assert embed.footer.icon_url is None


def test_dec_embed_docs_v1_5_correct_example(
    ts_interpreter: TagScriptInterpreter,
):
    script = textwrap.dedent(
        """
        {embed(author):some name|https://website.example}
        {embed(footer):some text|https://website.example/icon.png}
        """,
    ).strip()
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "some name"
    assert embed.author.url == "https://website.example"
    assert embed.author.icon_url is None
    assert embed.footer.text == "some text"
    assert embed.footer.icon_url == "https://website.example/icon.png"


# region Author attribute
@pytest.mark.parametrize(
    ("script", "name_out", "url_out", "icon_url_out"),
    (
        pytest.param(
            "{embed(author):this is a name}",
            "this is a name",
            None,
            None,
            id="name_only",
        ),
        pytest.param(
            "{embed(author):my name|https://website.example}",
            "my name",
            "https://website.example",
            None,
            id="name_and_url",
        ),
        pytest.param(
            "{embed(author):my name|https://website.example|https://website.example/icon}",
            "my name",
            "https://website.example",
            "https://website.example/icon",
            id="name_and_url_and_icon",
        ),
        pytest.param(
            "{embed(author):my name||https://website.example/icon}",
            "my name",
            None,
            "https://website.example/icon",
            id="name_and_icon",
        ),
        pytest.param(
            "{embed(author):|https://website.example|https://website.example/icon}",
            None,
            None,
            None,
            id="missing_name_but_both_urls_is_invalid",
        ),
        pytest.param(
            "{embed(author):|https://website.example}",
            None,
            None,
            None,
            id="missing_name_with_url_is_invalid",
        ),
        pytest.param(
            "{embed(author):||https://website.example/icon}",
            None,
            None,
            None,
            id="missing_name_with_icon_is_invalid",
        ),
        pytest.param(
            "{embed(author):}",
            None,
            None,
            None,
            id="empty_payload_is_invalid",
        ),
        pytest.param(
            "{embed(author)}",
            None,
            None,
            None,
            id="missing_payload_is_invalid",
        ),
    ),
)
def test_dec_embed_author_attr(
    script: str,
    name_out: str | None,
    url_out: str | None,
    icon_url_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == name_out
    assert embed.author.url == url_out
    assert embed.author.icon_url == icon_url_out


def test_dec_embed_author_attr_prevent_injection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):{username}|{my_url}}"
    data = {
        "username": adapters.StringAdapter("hello I have a | funky name"),
        "my_url": adapters.StringAdapter("https://website.example/page"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "hello I have a | funky name"
    assert embed.author.url == "https://website.example/page"
    assert embed.author.icon_url is None


@pytest.mark.parametrize(
    ("payload",),
    (
        pytest.param("the name|https://website.example/page", id="name_and_url"),
        pytest.param(
            "the name|https://website.example/page|https://website.example/icon.png",
            id="all_attributes",
        ),
        pytest.param(
            "the name||https://website.example/icon.png",
            id="name_and_icon_url",
        ),
    ),
)
def test_dec_embed_author_attr_ignore_nested_payload_and_take_all_for_name(
    payload: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):{my_payload}}"
    data = {"my_payload": adapters.StringAdapter(payload)}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    # no zero-depth "|" -> gets taken as "name only" configuration
    assert embed.author.name == payload
    assert embed.author.url is None
    assert embed.author.icon_url is None


# endregion


# region Description attribute
@pytest.mark.parametrize(
    ("script", "description_out"),
    (
        pytest.param(
            "{embed(description):This is my description.}",
            "This is my description.",
            id="valid",
        ),
        pytest.param("{embed(description):}", None, id="empty_payload_is_invalid"),
        pytest.param("{embed(description)}", None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_description_attr(
    script: str,
    description_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.description == description_out


# endregion


# region Title attribute
@pytest.mark.parametrize(
    ("script", "title_out"),
    (
        pytest.param(
            "{embed(title):This is my title.}",
            "This is my title.",
            id="valid",
        ),
        pytest.param("{embed(title):}", None, id="empty_payload_is_invalid"),
        pytest.param("{embed(title)}", None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_title_attr(
    script: str,
    title_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == title_out


# endregion


# region Colour/color attribute
@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
@pytest.mark.parametrize(
    ("col_name", "col_value"),
    (
        pytest.param("default", discord.Colour.default(), id="default"),
        pytest.param("teal", discord.Colour.teal(), id="teal"),
        pytest.param("dark_teal", discord.Colour.dark_teal(), id="dark_teal"),
        pytest.param("brand_green", discord.Colour.brand_green(), id="brand_green"),
        pytest.param("green", discord.Colour.green(), id="green"),
        pytest.param("dark_green", discord.Colour.dark_green(), id="dark_green"),
        pytest.param("blue", discord.Colour.blue(), id="blue"),
        pytest.param("dark_blue", discord.Colour.dark_blue(), id="dark_blue"),
        pytest.param("purple", discord.Colour.purple(), id="purple"),
        pytest.param("dark_purple", discord.Colour.dark_purple(), id="dark_purple"),
        pytest.param("magenta", discord.Colour.magenta(), id="magenta"),
        pytest.param("dark_magenta", discord.Colour.dark_magenta(), id="dark_magenta"),
        pytest.param("gold", discord.Colour.gold(), id="gold"),
        pytest.param("dark_gold", discord.Colour.dark_gold(), id="dark_gold"),
        pytest.param("orange", discord.Colour.orange(), id="orange"),
        pytest.param("dark_orange", discord.Colour.dark_orange(), id="dark_orange"),
        pytest.param("brand_red", discord.Colour.brand_red(), id="brand_red"),
        pytest.param("red", discord.Colour.red(), id="red"),
        pytest.param("dark_red", discord.Colour.dark_red(), id="dark_red"),
        pytest.param("lighter_grey", discord.Colour.lighter_grey(), id="lighter_grey"),
        pytest.param("lighter_gray", discord.Colour.lighter_gray(), id="lighter_gray"),
        pytest.param("dark_grey", discord.Colour.dark_grey(), id="dark_grey"),
        pytest.param("dark_gray", discord.Colour.dark_gray(), id="dark_gray"),
        pytest.param("light_grey", discord.Colour.light_grey(), id="light_grey"),
        pytest.param("light_gray", discord.Colour.light_gray(), id="light_gray"),
        pytest.param("darker_grey", discord.Colour.darker_grey(), id="darker_grey"),
        pytest.param("darker_gray", discord.Colour.darker_gray(), id="darker_gray"),
        pytest.param("og_blurple", discord.Colour.og_blurple(), id="og_blurple"),
        pytest.param("blurple", discord.Colour.blurple(), id="blurple"),
        pytest.param("greyple", discord.Colour.greyple(), id="greyple"),
        pytest.param("dark_theme", discord.Colour.dark_theme(), id="dark_theme"),
        pytest.param("fuchsia", discord.Colour.fuchsia(), id="fuchsia"),
        pytest.param("yellow", discord.Colour.yellow(), id="yellow"),
        pytest.param("dark_embed", discord.Colour.dark_embed(), id="dark_embed"),
        pytest.param("light_embed", discord.Colour.light_embed(), id="light_embed"),
        pytest.param("pink", discord.Colour.pink(), id="pink"),
        pytest.param(
            "ash_theme",
            discord.Colour.ash_theme(),
            marks=pytest.mark.skipif(
                discord.version_info[:2] < (2, 6),
                reason="new colour added in discord.py 2.6.0",
            ),
            id="ash_theme",
        ),
        pytest.param(
            "ash_embed",
            discord.Colour.ash_embed(),
            marks=pytest.mark.skipif(
                discord.version_info[:2] < (2, 6),
                reason="new colour added in discord.py 2.6.0",
            ),
            id="ash_embed",
        ),
        pytest.param(
            "onyx_theme",
            discord.Colour.onyx_theme(),
            marks=pytest.mark.skipif(
                discord.version_info[:2] < (2, 6),
                reason="new colour added in discord.py 2.6.0",
            ),
            id="onyx_theme",
        ),
        pytest.param(
            "onyx_embed",
            discord.Colour.onyx_embed(),
            marks=pytest.mark.skipif(
                discord.version_info[:2] < (2, 6),
                reason="new colour added in discord.py 2.6.0",
            ),
            id="onyx_embed",
        ),
    ),
)
def test_dec_embed_predefined_dpy_colour_support(
    col_attr_variant: str,
    col_name: str,
    col_value: discord.Colour,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant}):{col_name}}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    assert embed.colour is not None
    assert embed.color == col_value
    assert embed.color.value == col_value.value
    assert embed.colour == col_value
    assert embed.colour.value == col_value.value


@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
@pytest.mark.parametrize(
    ("payload", "output"),
    (
        pytest.param("r", 'Embed Parse Error: Colour "r" is invalid.', id="r_attr"),
        pytest.param("g", 'Embed Parse Error: Colour "g" is invalid.', id="g_attr"),
        # no test for b property because b can be a valid hex input
        pytest.param(
            "to_rgb",
            'Embed Parse Error: Colour "to_rgb" is invalid.',
            id="to_rgb_method",
        ),
        pytest.param(
            "#FFFFFFFF",
            'Embed Parse Error: Colour "ffffffff" is invalid.',
            id="hex_colour_with_alpha_channel",
        ),
    ),
)
def test_dec_embed_colour_attr_invalid_values(
    col_attr_variant: str,
    payload: str,
    output: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant}):{payload}}}"
    response = ts_interpreter.process(script)
    assert response.body == output
    embed = response.actions.get("embed")
    assert embed is None


@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
def test_dec_embed_colour_empty_payload_is_rejected(
    col_attr_variant: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant}):}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is None
    assert embed.colour is None


@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
def test_dec_embed_colour_missing_payload_is_rejected(
    col_attr_variant: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant})}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is None
    assert embed.colour is None


@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
def test_dec_embed_color_attr_random_color_is_supported(
    col_attr_variant: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant}):random}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    assert embed.colour is not None
    assert 0 <= embed.color.value <= 0xFFFFFF
    assert 0 <= embed.colour.value <= 0xFFFFFF


@pytest.mark.parametrize(
    "col_attr_variant",
    ("color", "colour"),
)
@pytest.mark.parametrize(
    ("col_input", "col_output"),
    (
        pytest.param("0xFFFFFF", int("FFFFFF", base=16), id="hex_number"),
        pytest.param("#FFFFFF", int("FFFFFF", base=16), id="hex_string"),
    ),
)
def test_dec_embed_color_attr_hex_colours_are_supported(
    col_attr_variant: str,
    col_input: str,
    col_output: int,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed({col_attr_variant}):{col_input}}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    assert embed.colour is not None
    assert embed.color.value == col_output
    assert embed.colour.value == col_output


# endregion


# region URL attribute
@pytest.mark.parametrize(
    ("script", "url_out"),
    (
        pytest.param(
            "{embed(url):https://website.example}",
            "https://website.example",
            id="valid",
        ),
        pytest.param("{embed(url):}", None, id="empty_payload_is_invalid"),
        pytest.param("{embed(url)}", None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_url_attr(
    script: str,
    url_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.url == url_out


# endregion


# region Thumbnail attribute
@pytest.mark.parametrize(
    ("script", "thumbnail_out"),
    (
        pytest.param(
            "{embed(thumbnail):https://website.example/icon.png}",
            "https://website.example/icon.png",
            id="valid",
        ),
        pytest.param("{embed(thumbnail):}", None, id="empty_payload_is_invalid"),
        pytest.param("{embed(thumbnail)}", None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_thumbnail_is_supported(
    script: str,
    thumbnail_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.thumbnail.url == thumbnail_out


# endregion


# region Image attribute
@pytest.mark.parametrize(
    ("script", "image_out"),
    (
        pytest.param(
            "{embed(image):https://website.example/img.png}",
            "https://website.example/img.png",
            id="valid",
        ),
        pytest.param("{embed(image):}", None, id="empty_payload_is_invalid"),
        pytest.param("{embed(image)}", None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_image_is_supported(
    script: str,
    image_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.image.url == image_out


# endregion


# region Fields
@pytest.mark.parametrize(
    ("inline_val", "inline_out"),
    (
        pytest.param("", False, id="missing_means_inline=False"),
        pytest.param("|true", True, id="true"),
        pytest.param("|false", False, id="false"),
    ),
)
def test_dec_embed_field_inlining(
    inline_val: str,
    inline_out: bool,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed(field):field name|field value{inline_val}}}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "field name"
    assert embed.fields[0].value == "field value"
    assert embed.fields[0].inline == inline_out


def test_dec_embed_field_invalid_inline_value_results_in_error_msg(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):field name|field value|messedupvalue}"
    response = ts_interpreter.process(script)
    assert (
        response.body
        == "Embed Parse Error: `inline` argument for `add_field` is not a boolean value (was `messedupvalue`)."
    )
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_field_payload_without_pipes_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):just one long unsplit payload}"
    response = ts_interpreter.process(script)
    assert response.body == "Embed Parse Error: `add_field` payload was not split by |."
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_fields_are_capped_at_25_fields(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{embed(field):field 00 name|field 00 value}"
        "{embed(field):field 01 name|field 01 value}"
        "{embed(field):field 02 name|field 02 value}"
        "{embed(field):field 03 name|field 03 value}"
        "{embed(field):field 04 name|field 04 value}"
        "{embed(field):field 05 name|field 05 value}"
        "{embed(field):field 06 name|field 06 value}"
        "{embed(field):field 07 name|field 07 value}"
        "{embed(field):field 08 name|field 08 value}"
        "{embed(field):field 09 name|field 09 value}"
        "{embed(field):field 10 name|field 10 value}"
        "{embed(field):field 11 name|field 11 value}"
        "{embed(field):field 12 name|field 12 value}"
        "{embed(field):field 13 name|field 13 value}"
        "{embed(field):field 14 name|field 14 value}"
        "{embed(field):field 15 name|field 15 value}"
        "{embed(field):field 16 name|field 16 value}"
        "{embed(field):field 17 name|field 17 value}"
        "{embed(field):field 18 name|field 18 value}"
        "{embed(field):field 19 name|field 19 value}"
        "{embed(field):field 20 name|field 20 value}"
        "{embed(field):field 21 name|field 21 value}"
        "{embed(field):field 22 name|field 22 value}"
        "{embed(field):field 23 name|field 23 value}"
        "{embed(field):field 24 name|field 24 value}"
        "{embed(field):field 25 name|field 25 value}"
    )
    response = ts_interpreter.process(script)
    assert (
        response.body
        == "Embed Parse Error: Maximum number of embed fields exceeded (25)."
    )
    embed = response.actions.get("embed")
    assert embed is not None
    assert len(embed.fields) == 25
    for i in range(25):
        assert embed.fields[i].name == f"field {i:02} name"
        assert embed.fields[i].value == f"field {i:02} value"


def test_dec_embed_fields_with_empty_payload_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):}"
    response = ts_interpreter.process(script)
    assert response.body == "Embed Parse Error: `add_field` payload was not split by |."
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_fields_with_missing_payload_are_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field)}"
    response = ts_interpreter.process(script)
    assert response.body == "Embed Parse Error: `add_field` missing payload."
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_field_prevent_injection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):{username}|{my_text}}"
    data = {
        "username": adapters.StringAdapter("hello I have a | funky name"),
        "my_text": adapters.StringAdapter("According to all known laws of aviation..."),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "hello I have a | funky name"
    assert embed.fields[0].value == "According to all known laws of aviation..."


@pytest.mark.parametrize(
    ("payload",),
    (
        pytest.param("the name|the value", id="no_inline"),
        pytest.param("the name|the value|true", id="inline_true"),
        pytest.param("the name|the value|false", id="inline_false"),
    ),
)
def test_dec_embed_field_disallow_nested_payload(
    payload: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):{my_payload}}"
    data = {"my_payload": adapters.StringAdapter(payload)}
    response = ts_interpreter.process(script, data)
    assert response.body == "Embed Parse Error: `add_field` payload was not split by |."
    embed = response.actions.get("embed")
    assert embed is None


# endregion


# region Footer attribute
@pytest.mark.parametrize(
    ("script", "text_out", "icon_url_out"),
    (
        pytest.param("{embed(footer):my text}", "my text", None, id="text_only"),
        pytest.param(
            "{embed(footer):my text|https://website.example/icon.png}",
            "my text",
            "https://website.example/icon.png",
            id="text_and_icon",
        ),
        pytest.param(
            "{embed(footer):my text|}",
            "my text",
            None,
            id="text_and_empty_icon",
        ),
        pytest.param(
            "{embed(footer):|https://website.example/icon.png}",
            None,
            "https://website.example/icon.png",
            id="empty_text_but_icon",
        ),
        pytest.param("{embed(footer):}", None, None, id="empty_payload_is_invalid"),
        pytest.param("{embed(footer)}", None, None, id="missing_payload_is_invalid"),
    ),
)
def test_dec_embed_footer_attr(
    script: str,
    text_out: str | None,
    icon_url_out: str | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == text_out
    assert embed.footer.icon_url == icon_url_out


def test_dec_embed_footer_attr_prevent_injection(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):{username}|{my_url}}"
    data = {
        "username": adapters.StringAdapter("hello I have a | funky name"),
        "my_url": adapters.StringAdapter("https://website.example/avatar.png"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == "hello I have a | funky name"
    assert embed.footer.icon_url == "https://website.example/avatar.png"


def test_dec_embed_footer_attr_ignore_nested_payload_and_take_all_for_text(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):{my_payload}}"
    data = {
        "my_payload": adapters.StringAdapter("text|https://website.example/icon.png"),
    }
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == "text|https://website.example/icon.png"
    assert embed.footer.icon_url is None


# endregion


# region Timestamp attribute
@pytest.mark.parametrize(
    ("script", "timestamp_out"),
    (
        pytest.param(
            "{embed(timestamp):1200000000}",
            datetime(2008, 1, 10, 21, 20, 0, tzinfo=UTC),
            id="timestamp_int",
        ),
        pytest.param(
            "{embed(timestamp):2022-02-22T22:22:22}",
            datetime(2022, 2, 22, 22, 22, 22, tzinfo=UTC),
            id="isoformat_no_offset",
        ),
        pytest.param(
            "{embed(timestamp):2022-02-22T22:22:22+01:00}",
            datetime(2022, 2, 22, 21, 22, 22, tzinfo=UTC),
            id="isoformat_with_offset",
        ),
        pytest.param("{embed(timestamp):}", None, id="empty_payload"),
        pytest.param("{embed(timestamp)}", None, id="missing_payload"),
        pytest.param(
            "{embed(timestamp):try parsing this to a valid datetime}",
            None,
            id="invalid_payload",
        ),
    ),
)
def test_dec_embed_timestamp_attr(
    script: str,
    timestamp_out: datetime | None,
    ts_interpreter: TagScriptInterpreter,
):
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.timestamp == timestamp_out


@pytest.mark.parametrize(
    "timestamp",
    (
        pytest.param("1200000000000", id="microseconds"),
        pytest.param("1200000000000000000", id="nanoseconds"),
    ),
)
def test_dec_embed_timestamp_attr_unsupported_timestamp_resolutions_return_error_msg(
    timestamp: str,
    ts_interpreter: TagScriptInterpreter,
):
    script = f"{{embed(timestamp):{timestamp}}}"
    response = ts_interpreter.process(script)
    assert response.body is not None
    # exact message depends on platform and which of the values is passed, this is fine
    assert response.body.startswith("Embed Parse Error: ")
    embed = response.actions.get("embed")
    assert embed is None


# endregion


# region JSON parsing
def test_dec_embed_json_parsing_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    # sample JSON that hits pretty much every embed attribute
    script = (
        "{embed("
        "{"
        '"url":"https://website.example/title",'
        '"timestamp":"2025-01-01T00:00:00.000Z",'
        '"title":"My title",'
        '"description":"This is my description",'
        '"thumbnail":{'
        '"url":"https://website.example/thumbnail.jpg"'
        "},"
        '"image":{'
        '"url":"https://website.example/image.png"'
        "},"
        '"author":{'
        '"name":"Author name",'
        '"url":"https://website.example/author",'
        '"icon_url":"https://website.example/author_icon.png"'
        "},"
        '"color":2829617,'
        '"fields":['
        '{"name":"Field name 00","value":"Field value 00","inline":true},'
        '{"name":"Field name 01","value":"Field value 01","inline":false},'
        '{"name":"Field name 02","value":"Field value 02"}'
        "],"
        '"footer":{'
        '"icon_url":"https://website.example/footer_icon.jpg",'
        '"text":"Footer text"'
        "}"  # footer end
        "}"  # JSON end
        ")}"  # param and block end
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.url == "https://website.example/title"
    assert isinstance(embed.timestamp, datetime)
    assert (
        embed.timestamp.isoformat(timespec="milliseconds") + "Z"
        == "2025-01-01T00:00:00.000Z"
    )
    # the Z is specifically stripped by discord.py
    assert embed.title == "My title"
    assert embed.description == "This is my description"
    assert embed.thumbnail.url == "https://website.example/thumbnail.jpg"
    assert embed.image.url == "https://website.example/image.png"
    assert embed.author.name == "Author name"
    assert embed.author.url == "https://website.example/author"
    assert embed.author.icon_url == "https://website.example/author_icon.png"
    assert embed.colour is not None
    assert embed.colour.value == 2829617
    assert embed.color is not None
    assert embed.color.value == 2829617
    assert len(embed.fields) == 3
    assert embed.fields[0].name == "Field name 00"
    assert embed.fields[0].value == "Field value 00"
    assert embed.fields[0].inline
    assert embed.fields[1].name == "Field name 01"
    assert embed.fields[1].value == "Field value 01"
    assert not embed.fields[1].inline
    assert embed.fields[2].name == "Field name 02"
    assert embed.fields[2].value == "Field value 02"
    assert embed.fields[2].inline is None
    assert embed.footer.icon_url == "https://website.example/footer_icon.jpg"
    assert embed.footer.text == "Footer text"


def test_dec_embed_embed_json_under_embed_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{embed("
        "{"
        '"embed":{'
        '"title": "my title",'
        '"description": "this is a description",'
        '"url": "https://website.example"'
        "}"
        "}"
        ")}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == "my title"
    assert embed.description == "this is a description"
    assert embed.url == "https://website.example"


def test_dec_embed_json_with_colour_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{embed("
        "{"
        '"title": "My title",'
        '"description": "My description",'
        '"colour": "#FF7900"'
        "}"
        ")}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == "My title"
    assert embed.description == "My description"
    assert embed.colour is not None
    assert embed.colour.value == int("0xFF7900", base=16)
    assert embed.color is not None
    assert embed.color.value == int("0xFF7900", base=16)


def test_dec_embed_invalid_json_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = '{embed({"key": value})}'
    response = ts_interpreter.process(script)
    assert (
        response.body == "Embed Parse Error: Expecting value: line 1 column 9 (char 8)"
    )


def test_dec_embed_too_large_embed_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(title):" + ("a" * 6500) + "}"
    response = ts_interpreter.process(script)
    assert response.body == "`MAX EMBED LENGTH REACHED (6500/6000)`"


def test_dec_embed_invalid_colour_gives_error_message(
    ts_interpreter: TagScriptInterpreter,
):
    script = '{embed({"colour": 1.5})}'
    response = ts_interpreter.process(script)
    assert response.body == (
        "Embed Parse Error: Received invalid type for colour key (expected "
        "Colour | str | int | None, got float)."
    )


# endregion
