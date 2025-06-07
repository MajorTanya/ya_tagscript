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
    obj = MagicMock(discord.Member)
    a = adapters.MemberAdapter(obj)
    # color, colour, global_name, nick, avatar, discriminator, joined_at, joinstamp,
    # mention, bot, top_role, roleids = 12 from MemberAdapter
    # id, created_at, timestamp, name = 4 from AttributeAdapter
    # 12 from MemberAdapter, 4 from AttributeAdapter = 16 attrs total
    assert len(a._attributes) == 16


def test_method_count_is_correct():
    obj = MagicMock(discord.Member)
    a = adapters.MemberAdapter(obj)
    assert len(a._methods) == 0


def test_no_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member}"
    obj = MagicMock(discord.Member)
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_empty_param_returns_str(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member()}"
    obj = MagicMock(discord.Member)
    obj.__str__.return_value = "obj dunder str"  # type: ignore
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "obj dunder str"


def test_id_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(id)}"
    obj = MagicMock(discord.Member, id=1)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1"


def test_id_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(id)}"
    obj = MagicMock(discord.User, id=1)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1"


def test_name_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(name)}"
    obj = MagicMock(discord.Member)
    obj.name = "user's name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "user's name"


def test_name_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(name)}"
    obj = MagicMock(discord.User)
    obj.name = "user's name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "user's name"


def test_created_at_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(created_at)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Member, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:02:02+00:00"


def test_created_at_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(created_at)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.User, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:02:02+00:00"


def test_timestamp_attr_based_on_created_at_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(timestamp)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Member, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_timestamp_attr_based_on_created_at_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(timestamp)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.User, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_color_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(color)}"
    obj = MagicMock(discord.Member, color="#FF7900")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "#FF7900"


def test_color_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(color)}"
    obj = MagicMock(discord.User, color="#FF7900")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "#FF7900"


def test_colour_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(colour)}"
    obj = MagicMock(discord.Member, colour="#FF7900")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "#FF7900"


def test_colour_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(colour)}"
    obj = MagicMock(discord.User, colour="#FF7900")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "#FF7900"


def test_global_name_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(global_name)}"
    obj = MagicMock(discord.Member, global_name="a_real_username")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "a_real_username"


def test_global_name_attr_falls_back_to_username_if_global_name_not_set(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(global_name)}"
    obj = MagicMock(discord.Member, global_name=None)
    obj.name = "the_user_name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "the_user_name"


def test_global_name_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(global_name)}"
    obj = MagicMock(discord.Member, global_name="a_real_username")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "a_real_username"


def test_global_name_attr_with_user_provided_falls_back_to_username_if_global_name_not_set(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(global_name)}"
    obj = MagicMock(discord.User, global_name=None)
    obj.name = "the_user_name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "the_user_name"


def test_nick_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(nick)}"
    obj = MagicMock(discord.Member, nick="nickname here")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "nickname here"


def test_nick_attr_falls_back_to_global_name_if_nick_not_set_and_global_name_available(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(nick)}"
    obj = MagicMock(discord.Member, nick=None, global_name="My Global Name")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "My Global Name"


def test_nick_attr_falls_back_to_username_if_nick_and_global_name_not_set(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(nick)}"
    obj = MagicMock(discord.Member, nick=None, global_name=None)
    obj.name = "the_user_name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "the_user_name"


def test_nick_attr_with_user_provided_falls_back_to_global_name(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(nick)}"
    obj = MagicMock(discord.User, global_name="My Global Name")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "My Global Name"


def test_nick_attr_with_user_provided_falls_back_to_username_if_global_name_not_set(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(nick)}"
    obj = MagicMock(discord.User, global_name=None)
    obj.name = "the_user_name"
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "the_user_name"


def test_avatar_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(avatar)}"
    avatar = MagicMock(discord.Asset, url="https://website.example/avatar.png")
    obj = MagicMock(discord.Member, display_avatar=avatar)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "https://website.example/avatar.png"


def test_avatar_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(avatar)}"
    avatar = MagicMock(discord.Asset, url="https://website.example/avatar.png")
    obj = MagicMock(discord.User, display_avatar=avatar)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "https://website.example/avatar.png"


def test_discriminator_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(discriminator)}"
    obj = MagicMock(discord.Member, discriminator=1234)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1234"


def test_discriminator_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(discriminator)}"
    obj = MagicMock(discord.User, discriminator=1234)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1234"


def test_joined_at_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(joined_at)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Member, joined_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:02:02+00:00"


def test_joined_at_attr_with_user_provided_falls_back_to_created_at(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(joined_at)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.User, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "2025-01-01 02:02:02+00:00"


def test_joinstamp_attr_based_on_joined_at_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(joinstamp)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.Member, joined_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_joinstamp_attr_with_user_provided_falls_back_to_created_at(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(joinstamp)}"
    dt = datetime(2025, 1, 1, 2, 2, 2, tzinfo=UTC)
    obj = MagicMock(discord.User, created_at=dt)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == str(int(dt.timestamp()))


def test_mention_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(mention)}"
    obj = MagicMock(discord.Member, mention="@thisisauser")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "@thisisauser"


def test_mention_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(mention)}"
    obj = MagicMock(discord.User, mention="@thisisauser")
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "@thisisauser"


def test_bot_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(bot)}"
    obj = MagicMock(discord.Member, bot=True)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "True"


def test_bot_attr_with_user_provided_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(bot)}"
    obj = MagicMock(discord.User, bot=True)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "True"


def test_top_role_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(top_role)}"
    role_obj = MagicMock(discord.Role)
    # attr fetch uses str(attr) which returns the role name for discord.Role
    role_obj.__str__.return_value = "role_obj dunder str"  # type: ignore
    obj = MagicMock(discord.Member, top_role=role_obj)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "role_obj dunder str"


def test_top_role_attr_with_user_provided_falls_back_to_empty_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(top_role)}"
    obj = MagicMock(discord.User)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_roleids_attr_is_supported(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(roleids)}"
    roles = [
        MagicMock(discord.Role, id=1),
        MagicMock(discord.Role, id=2),
        MagicMock(discord.Role, id=3),
    ]
    obj = MagicMock(discord.Member, roles=roles)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == "1 2 3"


def test_roleids_attr_with_user_provided_falls_back_to_empty_string(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(roleids)}"
    obj = MagicMock(discord.User)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_roleids_attr_is_supported_oops_no_roles(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(roleids)}"
    obj = MagicMock(discord.Member, roles=[])
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == ""


def test_invalid_attr_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(fancy)}"
    obj = MagicMock(discord.Member)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script


def test_invalid_attr_with_user_provided_is_rejected(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{member(fancy)}"
    obj = MagicMock(discord.User)
    data = {"member": adapters.MemberAdapter(obj)}
    result = ts_interpreter.process(script, data).body
    assert result == script
