from ast import Pass
from asyncio.windows_events import NULL
from email import message
import json
from pickle import TRUE
from unicodedata import name
from aiohttp import request
import discord
from discord.ext import commands

with open("config.json", "r") as f:
    config = json.load(f)
token = config["token"]
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=config["prefix"], intents=intents)

@bot.event
async def on_ready():
    print("kostlanovamama")

@bot.command()
async def req(ctx):
    if ctx.channel.id ==  config["ids"]["req_channel_id"]:
        embed_vypomoc = discord.Embed(
            title="Výpomoc",
            description="Klikni pro žádost o roli"
        )

        embed_tester = discord.Embed(
            title="Tester",
            description="Klikni pro žádost o roli"
        )

        msg_vypomoc = await ctx.send(embed=embed_vypomoc)
        msg_tester = await ctx.send(embed=embed_tester)

        await msg_tester.add_reaction("✅")
        await msg_vypomoc.add_reaction("✅")

        config["ids"]["tester"] = msg_tester.id
        config["ids"]["vypomoc"] = msg_vypomoc.id

        with open("config.json","w") as f:
            json.dump(config, f, indent=0)
        print(msg_tester.id)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.id != config["ids"]["bot_id"]:
        guild = bot.get_guild(config["ids"]["server-id"])
        channel = guild.get_channel(config["ids"]["req_log_id"])
        channel_req = guild.get_channel(config["ids"]["req_channel_id"])
        with open("requests.json", "r") as r:
            requests = json.load(r)
        with open("users.json", "r") as u:
            users = json.load(u)
        if payload.channel_id == config["ids"]["req_channel_id"]:
            if users[str(payload.member.id)]["requested"] == False:
                if payload.message_id == config["ids"]["tester"]:
                    print("tester")
                    msg = await channel.send(f"{payload.member.mention} tester")
                    requests[str(msg.id)] = {}
                    requests[str(msg.id)]["role"] = "tester"
                elif payload.message_id == config["ids"]["vypomoc"]:
                    print("vypomoc")
                    msg = await channel.send(f"{payload.member.mention} vypomoc")
                    requests[str(msg.id)] = {}
                    requests[str(msg.id)]["role"] = "vypomoc"
                requests[str(msg.id)]["user"] = payload.member.id
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                users[str(payload.member.id)]["requested"] = True

            else:
                message = await channel_req.fetch_message(payload.message_id)
                await message.remove_reaction(payload.emoji,payload.member)

        elif payload.channel_id == config["ids"]["req_log_id"]:
            guild = bot.get_guild(config["ids"]["server-id"])
            role = requests[str(payload.message_id)]["role"]
            message = await channel_req.fetch_message(config["ids"][role])
            member = guild.get_member(requests[str(payload.message_id)]["user"])
            await message.remove_reaction("✅",member)
            users[str(payload.member.id)]["requested"] = False
            if payload.emoji.name == "✅":
                print("ano")
                users[str(member.id)]["roles"][role] = True
                await member.add_roles(discord.utils.get(member.guild.roles, name=role))
            elif payload.emoji.name == "❌":
                print("nn")
            
        with open("users.json","w") as u:
            json.dump(users, u, indent=3)

        with open("requests.json","w") as r:
            json.dump(requests, r, indent=2)

@bot.event
async def on_member_join(member):
    guild = bot.get_guild(config["ids"]["server-id"])
    channel = guild.get_channel(config["ids"]["in-channel"])
    await channel.send(f"+{member.mention}")

    role = discord.utils.get(member.guild.roles, name="Fanousek")
    await member.add_roles(role)

    with open("users.json","r") as u:
        users = json.load(u)

    users[str(member.id)] = {}
    users[str(member.id)]["requested"] = False
    users[str(member.id)]["roles"] = {}
    users[str(member.id)]["roles"]["tester"] = False
    users[str(member.id)]["roles"]["vypomoc"] = False


    with open("users.json","w") as u:
        json.dump(users, u, indent=3)

@bot.event
async def on_member_remove(member):
    guild = bot.get_guild(config["ids"]["server-id"])
    channel = guild.get_channel(config["ids"]["out-channel"])
    await channel.send(f"-{member.mention}")

bot.run(token)
