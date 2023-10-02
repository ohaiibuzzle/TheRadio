import asyncio
import itertools
import json
import random
import time

import discord
from discord.ext import commands

from . import ytdlp_interface


class VoiceError(Exception):
    pass


class Song:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.source = None

    def create_embed(self):
        embed = discord.Embed(title=self.title, url=self.url)
        embed.set_author(name="Now Playing")
        embed.add_field(name="Duration", value=self.source.duration)
        embed.set_thumbnail(url=self.source.thumbnail)
        return embed


class LoopingQueue:
    def __init__(self, songs, shuffle=False):
        super().__init__()
        self.songs = songs
        self.index = 0
        self._shuffle = shuffle
        if shuffle:
            self.shuffle()

    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(
                itertools.islice(self, item.start, item.stop, item.step)
            )
        else:
            return self.songs[item]

    def __iter__(self):
        return self.songs.__iter__()

    def __len__(self):
        return len(self.songs)

    def remove(self, index):
        del self.songs[index]

    def get(self):
        if self.index >= len(self.songs):
            if self._shuffle:
                self.shuffle()
            self.index = 0
        song = self.songs[self.index]
        self.index += 1
        return song

    def shuffle(self):
        random.shuffle(self.songs)


class VoiceState:
    def __init__(self, bot: commands.Bot, ctx: commands.Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.voice_channel = None
        self.next = asyncio.Event()

        with open("config.json") as f:
            config = json.load(f)
            playlist = config["playlist"]
            self.playlist = LoopingQueue(
                [Song(**song) for song in playlist], shuffle=config["shuffle"]
            )

        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self._volume = 0.5

    def __del__(self):
        self.audio_player.cancel()

    async def audio_player_task(self):
        while True:
            if self.voice is None:
                await asyncio.sleep(1)
                continue
            self.next.clear()
            self.current = self.playlist.get()
            if self.current.source is not None:
                del self.current.source
            try:
                self.current.source = (
                    await ytdlp_interface.YTDLPSource.from_url(
                        self.current.url, loop=self.bot.loop
                    )
                )
                self.voice.play(self.current.source, after=self.play_next_song)
            except Exception as e:
                print(e)
                self.play_next_song()
            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            # raise VoiceError(str(error))
            print(f"Error encountered while playing: {error}")
            time.sleep(10)
        del self.current.source
        self.next.set()
