from unittest.mock import MagicMock

from discord import Member
from discord.ext import commands

from ya_tagscript import TagScriptInterpreter, adapters, blocks


def test_member_adapter_example():
    # necessarily just an approximation of the tagscript portions
    mock_dpy_ctx = MagicMock(spec=commands.Context)
    mock_dpy_ctx.author = MagicMock(spec=Member)
    mock_dpy_ctx.author.id = 123

    used_blocks = [
        blocks.StrictVariableGetterBlock(),
    ]
    interpreter = TagScriptInterpreter(blocks=used_blocks)
    script = "{user(id)}"

    seeds = {"user": adapters.MemberAdapter(mock_dpy_ctx.author)}
    response = interpreter.process(script, seed_variables=seeds)

    assert response.body == "123"
