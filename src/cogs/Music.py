import json
import discord
from discord.ext import commands
from utils import voice_states


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Create a dictionary to store the voice clients
        self.voice_clients = {}

        # Read the global configs to know what channels to join
        config = json.load(open("config.json"))
        self.voice_channels = config["voice_channels"]

    def get_voice_client(self, guild):
        # Check if the bot is already connected to a voice channel
        if guild.id in self.voice_clients:
            # If so, return the voice client
            return self.voice_clients[guild.id]
        # If not, return None
        return None

    # Event loop to join all the channels in the config
    # as soon as the bot is ready
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if channel.id in self.voice_channels:
                    # print(f"Joined {channel.name} in {guild.name}")
                    self.voice_clients[guild.id] = voice_states.VoiceState(
                        self.bot, channel
                    )
                    self.voice_clients[guild.id].voice_channel = channel
                    self.voice_clients[
                        guild.id
                    ].voice = await channel.connect()
                    await guild.change_voice_state(
                        channel=channel, self_mute=False, self_deaf=True
                    )

    @discord.slash_command()
    @commands.guild_only()
    async def playing(self, ctx):
        """
        Shows the currently playing song.
        """
        await ctx.defer()
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        return await ctx.respond(embed=voice_client.current.create_embed())

    @discord.slash_command()
    @commands.guild_only()
    async def next(self, ctx):
        """
        Skips the current song.
        """
        await ctx.defer()
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        voice_client.voice.stop()
        return await ctx.respond("Skipped song.")

    @discord.slash_command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def disconnect(self, ctx):
        """
        Disconnects the bot from the voice channel.
        """
        await ctx.defer()
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")
        await voice_client.voice.disconnect()
        del self.voice_clients[ctx.guild.id]
        return await ctx.respond("Disconnected.")

    @discord.slash_command()
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def reconnect(self, ctx):
        """
        Reconnects the bot to the voice channel for the current guild.
        """
        await ctx.defer()
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client is not None:
            await voice_client.voice.disconnect()
            del self.voice_clients[ctx.guild.id]

        for channel in ctx.guild.channels:
            if channel.id in self.voice_channels:
                self.voice_clients[ctx.guild.id] = voice_states.VoiceState(
                    self.bot, channel
                )
                self.voice_clients[ctx.guild.id].voice_channel = channel
                self.voice_clients[
                    ctx.guild.id
                ].voice = await channel.connect()
                self.voice_clients[ctx.guild.id].voice.self_deaf = True
                await ctx.guild.change_voice_state(
                    channel=channel, self_mute=False, self_deaf=True
                )
                return await ctx.respond("Reconnected.")


def setup(bot):
    bot.add_cog(Music(bot))
