import json
import os
import discord

try:
    import uvloop  # noqa: F401
except ImportError:
    pass

# Load config
with open("config.json") as f:
    config = json.load(f)

# Create bot
intents = discord.Intents.default()
intents.voice_states = True

token = config["token"]
prefix = config["prefix"]

bot = discord.Bot(intents=intents)

# Load cogs
for filename in os.listdir("./src/cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


bot.run(token)
