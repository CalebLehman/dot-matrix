import typing
import aiohttp

import discord

from util.config import config
from util.channel import get_bot_channel

GameName = typing.Literal['Drawful Animate']
GAME_DATA_BASE_URL = 'https://fishery.jackboxgames.com/artifact/gallery'
ARTIFACT_BASE_URL = 'https://s3.amazonaws.com/jbg-blobcast-artifacts'


class BadGameId(Exception):
    pass


class GameData():
    def __init__(self, game_url: str, game_id: str) -> None:
        self.game_url = game_url
        self.game_id = game_id

    CATEGORY_NAME = 'Text Channels'

    @classmethod
    async def send(cls, guild: discord.Guild, embed: discord.Embed, file: discord.File) -> None:
        channel = await get_bot_channel(guild, cls.CATEGORY_NAME, config.jackbox_channel)
        await channel.send(embed=embed, file=file)


async def fetch_game_data(game_url: str, game_id: str):
    url = '/'.join([GAME_DATA_BASE_URL, game_url, game_id])
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            try:
                return (await response.json())['gameData']
            except KeyError:
                raise BadGameId()


async def save_game_artifact(artifact_key: str, artifact_file: typing.BinaryIO) -> None:
    url = '/'.join([ARTIFACT_BASE_URL, artifact_key])
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            artifact_file.write(await response.read())
