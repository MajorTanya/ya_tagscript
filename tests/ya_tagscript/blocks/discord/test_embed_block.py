from datetime import datetime, timezone
from unittest.mock import MagicMock

import discord
import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks, interfaces, interpreter


@pytest.fixture
def ts_interpreter():
    b = [
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


def test_dec_embed_parameter_is_interpreted_normally(
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


# region Author attribute
def test_dec_embed_author_name_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):this is a name}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "this is a name"
    assert embed.author.url is None
    assert embed.author.icon_url is None


def test_dec_embed_author_name_and_url_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):my name|https://website.example}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "my name"
    assert embed.author.url == "https://website.example"
    assert embed.author.icon_url is None


def test_dec_embed_author_name_and_url_and_icon_url_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = (
        "{embed(author):my name|https://website.example|https://website.example/icon}"
    )
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "my name"
    assert embed.author.url == "https://website.example"
    assert embed.author.icon_url == "https://website.example/icon"


def test_dec_embed_author_name_and_icon_url_no_url_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):my name||https://website.example/icon}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name == "my name"
    assert embed.author.url is None
    assert embed.author.icon_url == "https://website.example/icon"


def test_dec_embed_author_missing_name_means_no_author_at_all_both_urls(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):|https://website.example/|https://website.example/icon}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name is None
    assert embed.author.url is None
    assert embed.author.icon_url is None


def test_dec_embed_author_missing_name_means_no_author_at_all_one_url(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):|https://website.example/}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name is None
    assert embed.author.url is None
    assert embed.author.icon_url is None


def test_dec_embed_author_with_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(author):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.author.name is None
    assert embed.author.url is None
    assert embed.author.icon_url is None


# endregion


# region Description attribute
def test_dec_embed_description_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(description):This is my description.}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.description == "This is my description."


def test_dec_embed_empty_description_means_no_description_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(description):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.description is None


def test_dec_embed_missing_description_means_no_description_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(description)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.description is None


# endregion


# region Title attribute
def test_dec_embed_title_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(title):My Title}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title == "My Title"


def test_dec_embed_empty_title_means_no_title_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(title):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title is None


def test_dec_embed_missing_title_means_no_title_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(title)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.title is None


# endregion


# region Color attribute
def test_dec_embed_color_with_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is None


def test_dec_embed_color_attr_r_property_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):r}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "r" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_color_attr_g_property_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):g}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "g" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


# no test for b property because b can be a valid hex input


def test_dec_embed_color_attr_to_rgb_method_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):to_rgb}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "to_rgb" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_color_attr_value_outside_rgb_range_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):#FFFFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "ffffffff" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_color_attr_random_color_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):random}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert 0 <= embed.color.value <= 0xFFFFFF


def test_dec_embed_color_attr_hex_digit_colours_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):0xFFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("FFFFFF", base=16)


def test_dec_embed_color_attr_hex_string_colours_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):#FFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("FFFFFF", base=16)


def test_dec_embed_color_attr_predefined_colour_default_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):default}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0", base=16)


def test_dec_embed_color_attr_predefined_colour_teal_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):teal}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x1ABC9C", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_teal_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_teal}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x11806A", base=16)


def test_dec_embed_color_attr_predefined_colour_brand_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):brand_green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x57F287", base=16)


def test_dec_embed_color_attr_predefined_colour_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x2ECC71", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x1F8B4C", base=16)


def test_dec_embed_color_attr_predefined_colour_blue_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):blue}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x3498DB", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_blue_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_blue}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x206694", base=16)


def test_dec_embed_color_attr_predefined_colour_purple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):purple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x9B59B6", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_purple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_purple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x71368A", base=16)


def test_dec_embed_color_attr_predefined_colour_magenta_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):magenta}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xE91E63", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_magenta_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_magenta}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xAD1457", base=16)


def test_dec_embed_color_attr_predefined_colour_gold_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):gold}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xF1C40F", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_gold_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_gold}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xC27C0E", base=16)


def test_dec_embed_color_attr_predefined_colour_orange_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):orange}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xE67E22", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_orange_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_orange}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xA84300", base=16)


def test_dec_embed_color_attr_predefined_colour_brand_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):brand_red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xED4245", base=16)


def test_dec_embed_color_attr_predefined_colour_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xE74C3C", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x992D22", base=16)


def test_dec_embed_color_attr_predefined_colour_lighter_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):lighter_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x95A5A6", base=16)


def test_dec_embed_color_attr_predefined_colour_lighter_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):lighter_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x95A5A6", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x607D8B", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x607D8B", base=16)


def test_dec_embed_color_attr_predefined_colour_light_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):light_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x979C9F", base=16)


def test_dec_embed_color_attr_predefined_colour_light_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):light_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x979C9F", base=16)


def test_dec_embed_color_attr_predefined_colour_darker_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):darker_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x546E7A", base=16)


def test_dec_embed_color_attr_predefined_colour_darker_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):darker_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x546E7A", base=16)


def test_dec_embed_color_attr_predefined_colour_og_blurple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):og_blurple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x7289DA", base=16)


def test_dec_embed_color_attr_predefined_colour_blurple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):blurple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x5865F2", base=16)


def test_dec_embed_color_attr_predefined_colour_greyple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):greyple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x99AAB5", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_theme_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_theme}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x313338", base=16)


def test_dec_embed_color_attr_predefined_colour_fuchsia_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):fuchsia}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xEB459E", base=16)


def test_dec_embed_color_attr_predefined_colour_yellow_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):yellow}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xFEE75C", base=16)


def test_dec_embed_color_attr_predefined_colour_dark_embed_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):dark_embed}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0x2B2D31", base=16)


def test_dec_embed_color_attr_predefined_colour_light_embed_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):light_embed}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xEEEFF1", base=16)


def test_dec_embed_color_attr_predefined_colour_pink_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(color):pink}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.color is not None
    # noinspection PyUnresolvedReferences
    assert embed.color.value == int("0xEB459F", base=16)


# endregion


# region Colour attribute
def test_dec_embed_colour_with_empty_payload_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is None


def test_dec_embed_colour_attr_r_property_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):r}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "r" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_colour_attr_g_property_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):g}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "g" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


# no test for b property because b can be a valid hex input


def test_dec_embed_colour_attr_to_rgb_method_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):to_rgb}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "to_rgb" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_colour_attr_value_outside_rgb_range_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):#FFFFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == 'Embed Parse Error: Colour "ffffffff" is invalid.'
    embed = response.actions.get("embed")
    assert embed is None


def test_dec_embed_colour_attr_random_color_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):random}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert 0 <= embed.colour.value <= 0xFFFFFF


def test_dec_embed_colour_attr_hex_digit_colours_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):0xFFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("FFFFFF", base=16)


def test_dec_embed_colour_attr_hex_string_colours_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):#FFFFFF}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("FFFFFF", base=16)


def test_dec_embed_colour_attr_predefined_colour_default_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):default}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0", base=16)


def test_dec_embed_colour_attr_predefined_colour_teal_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):teal}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x1ABC9C", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_teal_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_teal}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x11806A", base=16)


def test_dec_embed_colour_attr_predefined_colour_brand_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):brand_green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x57F287", base=16)


def test_dec_embed_colour_attr_predefined_colour_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x2ECC71", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_green_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_green}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x1F8B4C", base=16)


def test_dec_embed_colour_attr_predefined_colour_blue_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):blue}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x3498DB", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_blue_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_blue}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x206694", base=16)


def test_dec_embed_colour_attr_predefined_colour_purple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):purple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x9B59B6", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_purple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_purple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x71368A", base=16)


def test_dec_embed_colour_attr_predefined_colour_magenta_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):magenta}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xE91E63", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_magenta_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_magenta}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xAD1457", base=16)


def test_dec_embed_colour_attr_predefined_colour_gold_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):gold}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xF1C40F", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_gold_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_gold}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xC27C0E", base=16)


def test_dec_embed_colour_attr_predefined_colour_orange_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):orange}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xE67E22", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_orange_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_orange}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xA84300", base=16)


def test_dec_embed_colour_attr_predefined_colour_brand_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):brand_red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xED4245", base=16)


def test_dec_embed_colour_attr_predefined_colour_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xE74C3C", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_red_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_red}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x992D22", base=16)


def test_dec_embed_colour_attr_predefined_colour_lighter_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):lighter_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x95A5A6", base=16)


def test_dec_embed_colour_attr_predefined_colour_lighter_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):lighter_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x95A5A6", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x607D8B", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x607D8B", base=16)


def test_dec_embed_colour_attr_predefined_colour_light_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):light_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x979C9F", base=16)


def test_dec_embed_colour_attr_predefined_colour_light_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):light_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x979C9F", base=16)


def test_dec_embed_colour_attr_predefined_colour_darker_grey_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):darker_grey}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x546E7A", base=16)


def test_dec_embed_colour_attr_predefined_colour_darker_gray_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):darker_gray}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x546E7A", base=16)


def test_dec_embed_colour_attr_predefined_colour_og_blurple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):og_blurple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x7289DA", base=16)


def test_dec_embed_colour_attr_predefined_colour_blurple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):blurple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x5865F2", base=16)


def test_dec_embed_colour_attr_predefined_colour_greyple_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):greyple}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x99AAB5", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_theme_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_theme}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x313338", base=16)


def test_dec_embed_colour_attr_predefined_colour_fuchsia_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):fuchsia}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xEB459E", base=16)


def test_dec_embed_colour_attr_predefined_colour_yellow_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):yellow}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xFEE75C", base=16)


def test_dec_embed_colour_attr_predefined_colour_dark_embed_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):dark_embed}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0x2B2D31", base=16)


def test_dec_embed_colour_attr_predefined_colour_light_embed_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):light_embed}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xEEEFF1", base=16)


def test_dec_embed_colour_attr_predefined_colour_pink_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(colour):pink}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.colour is not None
    # noinspection PyUnresolvedReferences
    assert embed.colour.value == int("0xEB459F", base=16)


# endregion


# region URL attribute
def test_dec_embed_url_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(url):https://website.example}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.url == "https://website.example"


def test_dec_embed_empty_url_means_no_url_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(url):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.url is None


def test_dec_embed_missing_url_means_no_url_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(url)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.url is None


# endregion


# region Thumbnail attribute
def test_dec_embed_thumbnail_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(thumbnail):https://website.example/icon.png}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.thumbnail.url == "https://website.example/icon.png"


def test_dec_embed_empty_thumbnail_means_no_thumbnail_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(thumbnail):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.thumbnail.url is None


def test_dec_embed_missing_thumbnail_means_no_thumbnail_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(thumbnail)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.thumbnail.url is None


# endregion


# region Image attribute
def test_dec_embed_image_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(image):https://website.example/icon.png}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.image.url == "https://website.example/icon.png"


def test_dec_embed_empty_image_means_no_image_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(image):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.image.url is None


def test_dec_embed_missing_image_means_no_image_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(image)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.image.url is None


# endregion


# region Fields
def test_dec_embed_field_name_and_value_are_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):field name|field value}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "field name"
    assert embed.fields[0].value == "field value"
    assert not embed.fields[0].inline


def test_dec_embed_field_inline_true_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):field name|field value|true}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "field name"
    assert embed.fields[0].value == "field value"
    assert embed.fields[0].inline


def test_dec_embed_field_inline_false_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(field):field name|field value|false}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 1
    assert embed.fields[0].name == "field name"
    assert embed.fields[0].value == "field value"
    assert not embed.fields[0].inline


def test_dec_embed_field_invalid_inline_value_raises_error(
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
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert len(embed.fields) == 0


# endregion


# region Footer attribute
def test_dec_embed_footer_text_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):my text}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == "my text"


def test_dec_embed_footer_text_and_icon_url_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):my text|https://website.example/icon.png}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == "my text"
    assert embed.footer.icon_url == "https://website.example/icon.png"


def test_dec_embed_footer_text_but_missing_icon_url_means_no_icon_url(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):my text|}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text == "my text"
    assert embed.footer.icon_url is None


def test_dec_embed_footer_missing_text_with_icon_url_is_accepted(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):|https://website.example/icon.png}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text is None
    assert embed.footer.icon_url == "https://website.example/icon.png"


def test_dec_embed_footer_empty_payload_means_no_footer_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text is None
    assert embed.footer.icon_url is None


def test_dec_embed_footer_missing_payload_means_no_footer_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(footer)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.footer.text is None
    assert embed.footer.icon_url is None


# endregion


# region Timestamp attribute
def test_dec_embed_timestamp_timestamp_int_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp):1200000000}"
    dt = datetime(2008, 1, 10, 21, 20, 0, tzinfo=timezone.utc)
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert isinstance(embed.timestamp, datetime)
    assert embed.timestamp == dt


def test_dec_embed_timestamp_datetime_parsing_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp):2022-02-22T22:22:22}"
    dt = datetime(2022, 2, 22, 22, 22, 22, tzinfo=timezone.utc)
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert isinstance(embed.timestamp, datetime)
    assert embed.timestamp == dt


def test_dec_embed_timestamp_datetime_with_offset_parsing_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp):2022-02-22T22:22:22+01:00}"
    dt = datetime(2022, 2, 22, 21, 22, 22, tzinfo=timezone.utc)
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert isinstance(embed.timestamp, datetime)
    assert embed.timestamp == dt


def test_dec_embed_timestamp_empty_payload_means_no_timestamp_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp):}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.timestamp is None


def test_dec_embed_timestamp_missing_payload_means_no_timestamp_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp)}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.timestamp is None


def test_dec_embed_timestamp_invalid_payload_means_no_timestamp_at_all(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{embed(timestamp):try parsing this to a valid datetime}"
    response = ts_interpreter.process(script)
    assert response.body == ""
    embed = response.actions.get("embed")
    assert embed is not None
    assert isinstance(embed, discord.Embed)
    assert embed.timestamp is None


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
    # noinspection PyUnresolvedReferences
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
    # noinspection PyUnresolvedReferences
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
