import logging

from discord import app_commands
from discord import Intents, Interaction

from discord.ext import commands

log = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, prefix: str) -> None:
        self.is_synced = False
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents=Intents.default())

        @self.event
        async def on_ready() -> None:
            if not self.is_synced:
                log.info('Syncing tree')
                await self.tree.sync()
                self.is_synced = True
            if self.user is not None:
                log.info(f'Logged in as \'{self.user.name}\'')

        @self.event
        async def on_app_command_completion(interaction: Interaction, command: app_commands.Command) -> None:
            log.info(
                f'Ran \'{command.qualified_name} {list(interaction.namespace)}\''
                f' for \'{interaction.user}\' (ID {interaction.user.id})'
            )
