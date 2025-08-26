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
    return TagScriptInterpreter(b)


def test_attr_count_is_correct():
    obj = MagicMock(discord.Guild)
    a = adapters.GuildAdapter(obj)
    # icon, member_count, members, bots, humans, description = 6 from GuildAdapter
    # id, created_at, timestamp, name = 4 from AttributeAdapter
    # 6 from GuildAdapter, 4 from AttributeAdapter = 10 attrs total
    assert len(a._attributes) == 10


def test_method_count_is_correct():
    obj = MagicMock(discord.Guild)
    a = adapters.GuildAdapter(obj)
    # random member method = 1 from GuildAdapter
    # no methods = 0 from AttributeAdapter
    # 1 from GuildAdapter, 0 from AttributeAdapter = 1 method total
    assert len(a._methods) == 1


def test_no_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild}"
    obj = MagicMock(discord.Guild)
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_empty_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild()}"
    obj = MagicMock(discord.Guild)
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"my_guild": adapters.AttributeAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_id_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(id)}"
    obj = MagicMock(discord.Guild, id=123)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "123"


def test_name_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(name)}"
    obj = MagicMock(discord.Guild)
    obj.name = "this is a guild"
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "this is a guild"


def test_created_at_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(created_at)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Guild, created_at=dt)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:02:02+00:00"


def test_timestamp_attr_based_on_created_at_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(timestamp)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Guild, created_at=dt)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_icon_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(icon)}"
    obj = MagicMock(
        discord.Guild,
        icon=MagicMock(discord.Asset, url="https://website.example/icon.jpg"),
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "https://website.example/icon.jpg"


def test_members_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(members)}"
    obj = MagicMock(
        discord.Guild,
        member_count=3,
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "3"


def test_member_count_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(member_count)}"
    obj = MagicMock(member_count=3)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "3"


def test_bots_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(bots)}"
    obj = MagicMock(
        members=[
            MagicMock(discord.Member, id=1, bot=True),
            MagicMock(discord.Member, id=2, bot=False),
            MagicMock(discord.Member, id=3, bot=False),
        ],
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1"


def test_bots_attr_is_supported_oops_all_human(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(bots)}"
    obj = MagicMock(
        members=[
            MagicMock(discord.Member, id=1, bot=False),
            MagicMock(discord.Member, id=2, bot=False),
            MagicMock(discord.Member, id=3, bot=False),
        ],
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "0"


def test_humans_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(humans)}"
    obj = MagicMock(
        members=[
            MagicMock(discord.Member, id=1, bot=True),
            MagicMock(discord.Member, id=2, bot=True),
            MagicMock(discord.Member, id=3, bot=False),
        ],
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1"


def test_humans_attr_is_supported_oops_all_bots(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(humans)}"
    obj = MagicMock(
        members=[
            MagicMock(discord.Member, id=1, bot=True),
            MagicMock(discord.Member, id=2, bot=True),
            MagicMock(discord.Member, id=3, bot=True),
        ],
    )
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "0"


def test_description_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(description)}"
    obj = MagicMock(discord.Guild, description="cool description")
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "cool description"


def test_random_member_getter_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(random)}"
    member_list = [
        MagicMock(discord.Member, id=1, bot=True),
        MagicMock(discord.Member, id=2, bot=False),
        MagicMock(discord.Member, id=3, bot=False),
    ]
    obj = MagicMock(discord.Guild, members=member_list)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result in list(map(lambda m: str(m), member_list))
    assert result != member_list


def test_invalid_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{my_guild(fancy)}"
    obj = MagicMock(discord.Guild)
    data = {"my_guild": adapters.GuildAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script
