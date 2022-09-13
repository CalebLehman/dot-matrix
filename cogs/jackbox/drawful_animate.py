import logging
import pathlib
import tempfile

import discord

from cogs.jackbox.base import save_game_artifact, fetch_game_data, GameData

log = logging.getLogger(__name__)

GAME_URL = 'DrawfulAnimateGame'


class DrawfulAnimateGameData(GameData):
    def __init__(self, game_id: str) -> None:
        super().__init__(game_url=GAME_URL, game_id=game_id)

    async def send_all(self, interaction: discord.Interaction) -> None:
        game_data = await fetch_game_data(GAME_URL, self.game_id)
        with tempfile.TemporaryDirectory() as tempdir:
            for drawing in game_data:
                title = drawing['title']
                drawing_path = pathlib.Path(tempdir) / 'drawing.gif'
                with open(drawing_path.resolve(), 'wb') as drawing_file:
                    await save_game_artifact(drawing['twitterOptions']['imageGifUri'], drawing_file)
                embed = discord.Embed(color=discord.Color.blurple(), title=f'||{title}||')
                embed.set_image(url='attachment://drawing.gif')
                file = discord.File(drawing_path.resolve())
                await self.send(guild=interaction.guild, embed=embed, file=file)
