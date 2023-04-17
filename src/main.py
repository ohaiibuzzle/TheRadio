import json
import os
import discord

try:
    import uvloop  # noqa: F401
except ImportError:
    pass

# Check if config exists
if not os.path.exists("config.json"):
    print("Config file not found. Please create a config.json file.")
    exit(1)

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
