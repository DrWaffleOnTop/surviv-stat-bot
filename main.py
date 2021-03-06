# Main file for bot
# edit everything that has a fixed prefix

import discord
from discord.ext import commands
import os
import aiosqlite
import json
import nest_asyncio
nest_asyncio.apply()

# added vote command
async def get_pref(bot, msg):
    name = msg.guild.id
    conn = await aiosqlite.connect("servers.db")
    c = await conn.cursor()
    await c.execute("select prefix from servers where name = ?", [str(name)])
    cor_fetch = await c.fetchall()
    prefix = cor_fetch[0][0]
    return prefix


bot = commands.Bot(command_prefix=get_pref)


@bot.event
async def on_ready():
    print("Bot Is Running ...")
    conn = await aiosqlite.connect("servers.db")
    c = await conn.cursor()
    await c.execute(
        """CREATE TABLE IF NOT EXISTS SERVERS(
                NAME TEXT,
                CHANGER TEXT,
                PREFIX TEXT,
                CONFIG TEXT,
                CHANGER2 TEXT,
                GEN BOOL
                 )"""
    )
    await conn.commit()
    current_servers = [str(server.id) for server in bot.guilds]
    print(f"Bot is Running on {len(current_servers)}!")
    await c.execute("select name from servers")
    d = await c.fetchall()
    e = [i[0] for i in d]
    print(e)
    for s in current_servers:
        if s not in e:
            await c.execute(
                "insert into servers values (?, 'None', 's!', '', 'None', 1)", [str(s)]
            )
            await conn.commit()
    for old in e:
        if old not in current_servers:
            await c.execute("delete from servers where name = ?", [str(old)])
            await conn.commit()
    stream = discord.Streaming(
        name=f"s!help on {len(bot.guilds)} servers!",
        url="https://www.twitch.tv/survivstatbot",
    )
    await bot.change_presence(activity=stream)


@bot.event
async def on_guild_join(guild):
    # Inserts Values into the Server for info
    print(f"Bot was added to {guild} :)")
    conn = await aiosqlite.connect("servers.db")
    c = await conn.cursor()
    await c.execute("select name from servers")
    await c.execute(
        "insert into servers values (?, 'None', 's!', '', 'None', 1)", [str(guild.id)]
    )
    await conn.commit()


@bot.event
async def on_guild_remove(guild):
    print(f"Bot was removed from {guild} :(")
    # Removing that guild from table
    conn = await aiosqlite.connect("servers.db")
    c = await conn.cursor()
    id = guild.id
    await c.execute("delete from servers where name = ?", [str(id)])
    await conn.commit()


dont_load = ["playerutils.py"]
# Loading All Cogs
for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        if file not in dont_load:
            bot.load_extension(f"cogs.{file[:-3]}")



# Grabbing token
token = json.load(open("token.json", "r"))["bot_token"]

bot.run(token)

