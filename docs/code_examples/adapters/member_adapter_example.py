import discord
from discord.ext import commands

from ya_tagscript import TagScriptInterpreter, adapters, blocks

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

used_blocks = [
    blocks.StrictVariableGetterBlock(),
]
interpreter = TagScriptInterpreter(blocks=used_blocks)
script = "{user(id)}"


@bot.command()
@commands.guild_only()
async def test(ctx: commands.Context):
    if isinstance(ctx.author, discord.User):
        return await ctx.send("Guilds only, friend!")

    seeds = {
        "user": adapters.MemberAdapter(ctx.author),
    }
    response = interpreter.process(script, seed_variables=seeds)
    print(response.body)  # 123
    return await ctx.send(response.body)  # sends message "123" to the invoking channel


bot.run("token")  # use your own bot's token
