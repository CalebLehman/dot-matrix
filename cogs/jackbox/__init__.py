import logging

import discord
from discord import app_commands
from discord.ext import commands

from util.ui import ErrorEmbed, SuccessEmbed
from cogs.jackbox.base import BadGameId, GameName
from cogs.jackbox.database import jackbox_database
from cogs.jackbox.drawful_animate import DrawfulAnimateGameData

log = logging.getLogger(__name__)


class BadGameType(Exception):
    pass


class JackboxCog(commands.GroupCog, name='jackbox'):
    def __init__(self) -> None:
        super().__init__()

    CATEGORY_NAME = 'Text Channels'

    @app_commands.command(name='about', description='Information about the `jackbox` group')
    async def about_command(self, interaction: discord.Interaction) -> None:
        description = '''
A group of commands for fetch artifacts from Jackbox games. \
Commands have autocomplete for the supported game types \
and when needed you can find the game id of the particular game \
by checking the URL of the page for the game in the *PAST GAMES* section on [jackbox.tv](https://jackbox.tv).

To see the available commands, type `/jackbox` and look through the autocomplete options.
'''
        embed = discord.Embed(title='About `jackbox`', description=description)
        embed.set_image(url='attachment://about.jpg')
        file = discord.File('cogs/jackbox/assets/about.jpg')
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name='artifacts', description='Fetch artifacts (e.g. GIFs) from a supported Jackbox game')
    async def events_command(self, interaction: discord.Interaction, game_name: GameName, game_id: str) -> None:
        op = 'artifacts'
        if jackbox_database.game_exists(id=game_id):
            embed = ErrorEmbed(op=op, reason=f'Already fetched artifacts from a game with ID {game_id}')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            match game_name:
                case 'Drawful Animate':
                    await DrawfulAnimateGameData(game_id).send_all(interaction)
                case _:
                    raise BadGameType()
            jackbox_database.create_game(id=game_id, name=game_name)
            embed = SuccessEmbed(op=op, reason=f'Fetched artifacts from game of type *{game_name}* with ID {game_id}')
            await interaction.followup.send(embed=embed, ephemeral=True)
        except BadGameId:
            embed = ErrorEmbed(op=op, reason=f'No game of type *{game_name}* with ID {game_id}')
            await interaction.followup.send(embed=embed, ephemeral=True)
        except BadGameType:
            embed = ErrorEmbed(op=op, reason=f'*{game_name}* is not a valid game type')
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(JackboxCog())
