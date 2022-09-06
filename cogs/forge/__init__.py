import logging
from datetime import date

from discord import app_commands, Color, Embed, File, Interaction
from discord.ext import tasks
from discord.ext.commands import Bot, GroupCog

from cogs.forge.scraper import get_events, FORGE_URL, Event

log: logging.Logger = logging.getLogger(__name__)

QUERY_INTERVAL_HOURS = 1


def describe_event(event: Event):
    days_length = 3
    try:
        days_until = (date.fromisoformat(event.date) - date.today()).days
    except ValueError:
        log.warn(f'Unable to parse date \'{event.date}\' for event \'{event.name}\'')
        days_until = '?' * days_length
    return f'`in {days_until:{days_length}} days` [{event.name}]({event.link})'


class ForgeCog(GroupCog, name='forge'):
    def __init__(self) -> None:
        self.events = []
        self.update_events.start()

    @tasks.loop(hours=QUERY_INTERVAL_HOURS)
    async def update_events(self) -> None:
        self.events = await get_events()

    def cog_unload(self):
        self.update_events.cancel()

    @app_commands.command(name='about', description='Information about the `forge` group')
    async def about_command(self, interaction: Interaction) -> None:
        description = f'''
A group of commands for checking on events at **The Forge Tavern**. \
The bot automatically checks for new events every {QUERY_INTERVAL_HOURS} hour(s). \
To see the available commands, type `/forge` and look through the autocomplete options.
'''
        embed: Embed = Embed(title='About `forge`', description=description)
        embed.set_image(url='attachment://about.png')
        file = File('cogs/forge/assets/about.png')
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name='events', description='Lists all upcoming events')
    async def events_command(self, interaction: Interaction) -> None:
        if len(self.events) == 0:
            embed = Embed(
                title='No upcoming events at The Forge Tavern',
                description=f'Events are pulled every {QUERY_INTERVAL_HOURS} hour(s) from {FORGE_URL}',
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            description = '>>> ' + '\n'.join([describe_event(event) for event in self.events])
            embed = Embed(title='Upcoming events at The Forge Tavern', description=description, color=Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(ForgeCog())
