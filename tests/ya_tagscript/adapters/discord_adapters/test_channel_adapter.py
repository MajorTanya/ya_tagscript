from datetime import UTC, datetime
from unittest.mock import MagicMock

import discord
import pytest

from ya_tagscript import TagScriptInterpreter, adapters, blocks


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.StrictVariableGetterBlock(),
    ]
    return TagScriptInterpreter(blocks=b)


def test_non_text_channel_is_not_accepted_but_retains_base_attrs(
    ts_interpreter: TagScriptInterpreter,
):
    dt = datetime(2025, 1, 1, 2, 3, 4, tzinfo=UTC)
    obj = MagicMock(discord.ForumChannel, id=1, created_at=dt)
    obj.name = "ch name"
    non_text_ch_adapter = adapters.ChannelAdapter(obj)

    # check attr and method counts, confirming only base is available
    assert len(non_text_ch_adapter._attributes) == 4
    assert len(non_text_ch_adapter._methods) == 0

    data = {"my_non_ch": non_text_ch_adapter}

    # check allowed attrs
    script = "{my_non_ch(id)}"
    result = ts_interpreter.process(script, data).body
    assert result == "1"
    script = "{my_non_ch(name)}"
    result = ts_interpreter.process(script, data).body
    assert result == "ch name"
    script = "{my_non_ch(created_at)}"
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:03:04+00:00"
    script = "{my_non_ch(timestamp)}"
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))

    # mixed
    script = "{my_non_ch(timestamp)}{my_non_ch(nsfw)}"
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp())) + "{my_non_ch(nsfw)}"

    # check unsupported
    script = "{my_non_ch(nsfw)}"
    result = ts_interpreter.process(script, data).body
    assert result == script
    script = "{my_non_ch(mention)}"
    result = ts_interpreter.process(script, data).body
    assert result == script
    script = "{my_non_ch(topic)}"
    result = ts_interpreter.process(script, data).body
    assert result == script
    script = "{my_non_ch(slowmode)}"
    result = ts_interpreter.process(script, data).body
    assert result == script
    script = "{my_non_ch(position)}"
    result = ts_interpreter.process(script, data).body
    assert result == script


def test_attr_count_is_correct():
    obj = MagicMock(discord.TextChannel)
    a = adapters.ChannelAdapter(obj)
    # nsfw, mention, topic, slowmode, position = 5 from ChannelAdapter
    # id, created_at, timestamp, name = 4 from AttributeAdapter
    # 5 from ChannelAdapter, 4 from AttributeAdapter = 9 attrs total
    assert len(a._attributes) == 9


def test_method_count_is_correct():
    obj = MagicMock(discord.TextChannel)
    a = adapters.ChannelAdapter(obj)
    assert len(a._methods) == 0


def test_nsfw_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(nsfw)}"
    obj = MagicMock(discord.TextChannel, nsfw=True)
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "True"


def test_mention_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(mention)}"
    obj = MagicMock(discord.TextChannel, mention="@channel")
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "@channel"


def test_topic_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(topic)}"
    obj = MagicMock(discord.TextChannel, topic="current channel topic")
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "current channel topic"


def test_topic_attr_falls_back_to_empty_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(topic)}"
    obj = MagicMock(discord.TextChannel, topic=None)
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_slowmode_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(slowmode)}"
    obj = MagicMock(discord.TextChannel, slowmode_delay=60)
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "60"


def test_position_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_ch(position)}"
    obj = MagicMock(discord.TextChannel, position=3)
    data = {"my_ch": adapters.ChannelAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "3"
