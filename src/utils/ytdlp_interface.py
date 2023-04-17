import yt_dlp
import discord
import asyncio

YTDLP_OPTIONS = {
    "format": "bestaudio/best",
    "outtmpl": "%(id)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTS = {
    "before_options": "-loglevel quiet -reconnect 1 -reconnect_streamed 1\
          -reconnect_delay_max 5 -reconnect_on_network_error 1\
              -reconnect_on_http_error 1",
    "options": "-vn",
}

yt_dlp_client = yt_dlp.YoutubeDL(YTDLP_OPTIONS)


class YTDLPSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("webpage_url")
        self.thumbnail = data.get("thumbnail")
        self.uploader = data.get("uploader")
        self.uploader_url = data.get("uploader_url")
        self.uploader_thumbnail = data.get("uploader_thumbnail")

        try:
            self.duration = data.get("duration_string")
        except AttributeError:
            self.duration = 0

    def __str__(self):
        return f"**{self.title}** by **{self.uploader}**"

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: yt_dlp_client.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = (
            data["url"] if stream else yt_dlp_client.prepare_filename(data)
        )
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTS), data=data)

    @classmethod
    async def parse_duration(duration: int):
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60

        if hours > 0:
            return f"{hours}:{minutes:02}:{seconds:02}"
        else:
            return f"{minutes}:{seconds:02}"
