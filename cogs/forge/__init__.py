import logging
import datetime
import zoneinfo

import discord
from discord import app_commands
from discord.ext import tasks, commands

from cogs.forge.scraper import get_events, FORGE_URL, Event

log = logging.getLogger(__name__)

QUERY_INTERVAL_HOURS = 1


def describe_event(event: Event):
    days_length = 3
    try:
        # TODO Seems like the timezone can be scraped from event.start, but
        #   - 1) don't want to rely on that element's format
        #   - 2) the Forge website seems to always use EDT, which ZoneInfo doesn't understand anyways
        tz = zoneinfo.ZoneInfo('US/Eastern')
        days_until = (datetime.date.fromisoformat(event.date) - datetime.datetime.now(tz=tz).date()).days
    except ValueError:
        log.warn(f'Unable to parse date \'{event.date}\' for event \'{event.name}\'')
        days_until = '?' * days_length
    return f'`in {days_until:{days_length}} days` [{event.name}]({event.link})'


class ForgeCog(commands.GroupCog, name='forge'):
    def __init__(self) -> None:
        self.events = []
        self.update_events.start()

    @tasks.loop(hours=QUERY_INTERVAL_HOURS)
    async def update_events(self) -> None:
        self.events = await get_events()
        log.info(f'Retrieved {len(self.events)} events from {FORGE_URL}')

    def cog_unload(self):
        self.update_events.cancel()

    @app_commands.command(name='about', description='Information about the `forge` group')
    async def about_command(self, interaction: discord.Interaction) -> None:
        description = f'''
A group of commands for checking on events at **The Forge Tavern**. \
The bot automatically checks [here]({FORGE_URL}) for new events every {QUERY_INTERVAL_HOURS} hour(s).

To see the available commands, type `/forge` and look through the autocomplete options.
'''
        embed = discord.Embed(title='About `forge`', description=description)
        embed.set_image(url='attachment://about.png')
        file = discord.File('cogs/forge/assets/about.png')
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name='events', description='Lists all upcoming events')
    async def events_command(self, interaction: discord.Interaction) -> None:
        if len(self.events) == 0:
            embed = discord.Embed(
                title='No upcoming events at The Forge Tavern',
                description=f'Events are pulled every {QUERY_INTERVAL_HOURS} hour(s) from {FORGE_URL}',
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            description = '>>> ' + '\n'.join([describe_event(event) for event in self.events])
            embed = discord.Embed(
                title='Upcoming events at The Forge Tavern',
                description=description,
                color=discord.Color.blurple(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ForgeCog())
