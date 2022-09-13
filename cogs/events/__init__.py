import logging
from urllib.parse import quote_plus

import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

from util.ui import ErrorEmbed, SuccessEmbed
from util.config import config
from util.channel import get_bot_channel
from cogs.events.database import events_database

log = logging.getLogger(__name__)


class AddGuestModal(ui.Modal):
    def __init__(self, event_id: int, location: str) -> None:
        super().__init__(title='Add a Guest')
        self.event_id = event_id
        self.location = location

    guest_name = ui.TextInput(
        label='Enter the name of the guest',
        style=discord.TextStyle.short,
        placeholder='name of guest',
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        guest = self.guest_name.value
        if guest in events_database.get_guests(event_id=self.event_id):
            embed = discord.Embed(title=f'{guest} is already added', color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            events_database.create_guest(name=self.guest_name.value, event_id=self.event_id)
            event_embed = EventEmbed(event_id=self.event_id)
            event_view = EventView(event_id=self.event_id, location=self.location)
            message = await interaction.channel.fetch_message(events_database.get_event_message(id=self.event_id))
            await message.edit(embed=event_embed, view=event_view)
            embed = discord.Embed(title=f'Added guest \'{self.guest_name}\'')
            await interaction.response.send_message(embed=embed, ephemeral=True)


class RemoveGuestModal(ui.Modal):
    def __init__(self, event_id: int, location: str) -> None:
        super().__init__(title='Remove a Guest')
        self.event_id = event_id
        self.location = location

    guest_name = ui.TextInput(
        label='Enter the name of the guest',
        style=discord.TextStyle.short,
        placeholder='name of guest',
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        events_database.delete_guest(name=self.guest_name.value, event_id=self.event_id)
        event_embed = EventEmbed(event_id=self.event_id)
        event_view = EventView(event_id=self.event_id, location=self.location)
        message = await interaction.channel.fetch_message(events_database.get_event_message(id=self.event_id))
        await message.edit(embed=event_embed, view=event_view)
        embed = discord.Embed(title=f'Removed guest(s) with name \'{self.guest_name}\'')
        await interaction.response.send_message(embed=embed, ephemeral=True)


class EventView(ui.View):
    def __init__(self, event_id: int, location: str) -> None:
        super().__init__(timeout=None)
        self.add_item(ui.Button(
            label='Google Maps',
            url=f'https://www.google.com/maps/search/?api=1&query={quote_plus(location)}',
            row=0,
        ))
        self.event_id = event_id
        self.location = location

    @ui.button(label='Add Guest', style=discord.ButtonStyle.green, row=0, custom_id='event_view:add')
    async def add(self, interaction: discord.Interaction, button: ui.Button) -> None:
        await interaction.response.send_modal(AddGuestModal(self.event_id, self.location))

    @ui.button(label='Remove Guest', style=discord.ButtonStyle.red, row=0, custom_id='event_view:remove')
    async def remove(self, interaction: discord.Interaction, button: ui.Button) -> None:
        await interaction.response.send_modal(RemoveGuestModal(self.event_id, self.location))


class EventEmbed(discord.Embed):
    def __init__(self, event_id) -> None:
        guests = events_database.get_guests(event_id)
        super().__init__(title=f'Guests [`+{len(guests)}`]', description=', '.join(guests))


class EventsCog(commands.GroupCog, name='events'):
    def __init__(self) -> None:
        super().__init__()

    CATEGORY_NAME = 'Text Channels'

    @classmethod
    async def remove_event(cls, guild: discord.Guild, event_id: int) -> None:
        try:
            message_id = events_database.get_event_message(id=event_id)
            events_database.delete_event(id=event_id)
            events_database.delete_guests(event_id=event_id)
        except Exception:
            log.warn(f'Failed to get message id for event with ID {event_id}')
            return
        channel = await get_bot_channel(guild, cls.CATEGORY_NAME, config.event_channel)
        try:
            message = await channel.fetch_message(message_id)
            await message.delete()
        except Exception:
            log.warn(f'Unable to delete message with ID {message_id} (probably already deleted)')
        try:
            thread = channel.get_thread(message_id)
            await thread.delete()
        except Exception:
            log.warn(f'Unable to delete thread with ID {message_id} (probably already deleted)')

    @classmethod
    async def create_event(cls, event: discord.ScheduledEvent) -> None:
        events_channel = await get_bot_channel(event.guild, cls.CATEGORY_NAME, config.event_channel)
        event_embed = EventEmbed(event_id=event.id)
        event_view = EventView(event_id=event.id, location=event.location)
        event_message = await events_channel.send(content=event.url, embed=event_embed, view=event_view)
        try:
            events_database.create_event(id=event.id, message_id=event_message.id)
        except Exception:
            log.warn(f'Event with id {event.id} is already in database, updating message id')
            events_database.delete_event(id=event.id)
            events_database.create_event(id=event.id, message_id=event_message.id)
        event_thread = await event_message.create_thread(name=f'{event.name} Discussion')
        warning_description = '''
This is a **temporary** thread and **will be deleted** when the event is over.
The intended use is for stuff like:
```
  - I'm running a little late, be there in 5 min
  - Should I eat first, or will we get food there?
  - Can I bring a new friend?
```
'''
        warning_embed = discord.Embed(
            title='**Warning**',
            description=warning_description,
            color=discord.Color.yellow(),
        )
        await event_thread.send(embed=warning_embed)

    @commands.GroupCog.listener(name='on_scheduled_event_create')
    async def on_event_create(self, event: discord.ScheduledEvent) -> None:
        await EventsCog.create_event(event)

    @commands.GroupCog.listener(name='on_scheduled_event_delete')
    async def on_event_delete(self, event: discord.ScheduledEvent) -> None:
        await EventsCog.remove_event(guild=event.guild, event_id=event.id)

    @commands.GroupCog.listener(name='on_scheduled_event_update')
    async def on_event_update(self, before: discord.ScheduledEvent, after: discord.ScheduledEvent) -> None:
        remove_status = [discord.EventStatus.completed, discord.EventStatus.cancelled]
        if (before.status not in remove_status) and (after.status in remove_status):
            await EventsCog.remove_event(guild=after.guild, event_id=after.id)
        elif (before.status in remove_status) and (after.status not in remove_status):
            await EventsCog.create_event(after)

    @app_commands.command(name='about', description='Information about the `events` group')
    async def about_command(self, interaction: discord.Interaction) -> None:
        pass

    @app_commands.command(name='register', description='Manually register an event')
    async def register_command(self, interaction: discord.Interaction, event_id: str) -> None:
        op = 'register'
        try:
            int_event_id = int(event_id)
        except ValueError:
            embed = ErrorEmbed(op=op, reason=f'Failed to parse event ID {event_id} (could not convert to integer)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if events_database.event_exists(int_event_id):
            embed = ErrorEmbed(op=op, reason=f'Failed to register event with ID {event_id} (already registered)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        event = interaction.guild.get_scheduled_event(int_event_id)
        if event is None:
            embed = ErrorEmbed(op=op, reason=f'Failed to register event with ID {int_event_id} (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await EventsCog.create_event(event)
        embed = SuccessEmbed(op=f'events {op}', reason=f'Registered existing event with ID {int_event_id}')
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='clean', description='Manually clean an event')
    async def clean_command(self, interaction: discord.Interaction, event_id: str) -> None:
        op = 'clean'
        try:
            int_event_id = int(event_id)
        except ValueError:
            embed = ErrorEmbed(op=op, reason=f'Failed to parse event ID {event_id} (could not convert to integer)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await EventsCog.remove_event(guild=interaction.guild, event_id=int_event_id)
        embed = SuccessEmbed(op=f'events {op}', reason=f'Cleaned event with ID {int_event_id}')
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventsCog())
