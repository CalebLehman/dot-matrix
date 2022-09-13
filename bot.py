import logging

import discord
from discord import app_commands
from discord import ui

from discord.ext import commands

log = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, prefix: str) -> None:
        self.is_synced = False
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents=intents)

        group = app_commands.Group(name='dot', description='Group of general bot commands')

        @group.command(name='about', description='Information about the Dot Matrix bot')
        async def about_command(interaction: discord.Interaction) -> None:
            description = '''
A [Discord Bot](https://discord.com/developers/docs/intro#bots-and-apps) for whatever!

Current command groups are `dot`, `address`, `forge`, `events`, and `jackbox`. \
Use `/<group> about` to learn more about a particular group, \
or just type `/<group>` and look at the autocomplete options.
'''
            embed = discord.Embed(title='About **Dot Matrix**', description=description)
            embed.set_image(url='attachment://dot_matrix.png')
            file = discord.File('assets/dot_matrix.png')
            view = ui.View()
            button = ui.Button(
                label='GitHub',
                url='https://github.com/CalebLehman/dot-matrix',
                style=discord.ButtonStyle.link,
            )
            view.add_item(button)
            await interaction.response.send_message(embed=embed, view=view, file=file, ephemeral=True)

        self.tree.add_command(group)

        @self.event
        async def on_ready() -> None:
            if not self.is_synced:
                log.info('Syncing tree')
                await self.tree.sync()
                self.is_synced = True
            if self.user is not None:
                log.info(f'Logged in as \'{self.user.name}\'')

        @self.event
        async def on_app_command_completion(interaction: discord.Interaction, command: app_commands.Command) -> None:
            name = command.qualified_name
            args = list(interaction.namespace)
            log.info(f'Ran \'{name} {args}\' for \'{interaction.user}\' (ID {interaction.user.id})')
