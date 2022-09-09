from typing import Optional
from urllib.parse import quote_plus

import discord
from discord import ui
from discord import app_commands
from discord.ext import commands

from util.ui import ErrorEmbed, SuccessEmbed
from cogs.address.database import address_database


class AddressEmbed(SuccessEmbed):
    def __init__(self, op: str, name: str, location: Optional[str] = None) -> None:
        if location is not None:
            description = f'''
>>> **{name}**
{location}
'''
            super().__init__(op=f'address {op}', reason=description)
        else:
            super().__init__(op=f'address {op}', reason=f'>>> **{name}**')


class AddressView(ui.View):
    def __init__(self, location: str) -> None:
        super().__init__()
        self.add_item(ui.Button(
            label='Google Maps',
            url=f'https://www.google.com/maps/search/?api=1&query={quote_plus(location)}',
            style=discord.ButtonStyle.link,
        ))


class AddressCog(commands.GroupCog, name='address'):
    def __init__(self) -> None:
        self.autocomplete_cache = None
        super().__init__()

    @app_commands.command(name='about', description='Information about the `address` group')
    async def about_command(self, interaction: discord.Interaction) -> None:
        description = '''
A group of commands for managing a **collection of addresses**. \
The **goal** is to eliminate the need for all *what was your address again?*-type questions in the chat.

To see the available commands, type `/address` and look through the autocomplete options.
'''
        embed = discord.Embed(title='About `address`', description=description)
        embed.set_image(url='attachment://about.png')
        file = discord.File('cogs/address/assets/about.png')
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name='set', description='Set a new address')
    async def set_command(self, interaction: discord.Interaction, name: str, location: str) -> None:
        op = 'set'
        if address_database.address_exists(name):
            embed = ErrorEmbed(op=op, reason=f'Failed to set new address *{name}* (already exists)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        address_database.create_address(name, location)
        name, location = address_database.get_address(name)
        embed = AddressEmbed(op=op, name=name, location=location)
        view = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='update', description='Update an existing addres')
    async def update_command(
        self,
        interaction: discord.Interaction,
        old_name: str,
        new_name: Optional[str],
        new_location: Optional[str],
    ) -> None:
        op = 'update'
        if new_name is None and new_location is None:
            embed = ErrorEmbed(op=op, reason='Failed to update because no updates were provided')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        new_name = new_name or old_name
        if not address_database.address_exists(old_name):
            embed = ErrorEmbed(op=op, reason=f'Failed to update address *{old_name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if new_name is not None and new_name.lower() != old_name.lower() and address_database.address_exists(new_name):
            embed = ErrorEmbed(
                op=op,
                reason=f'Failed to update address *{old_name}* to *{new_name}* (already exists)',
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        address_database.update_address(old_name, new_name, new_location)
        name: str
        location: str
        name, location = address_database.get_address(new_name)
        embed = AddressEmbed(op=op, name=name, location=location)
        view = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='get', description='Get an existing address')
    async def get_command(self, interaction: discord.Interaction, name: str) -> None:
        op = 'get'
        if not address_database.address_exists(name):
            embed = ErrorEmbed(op=op, reason=f'Failed to get address *{name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        location: str
        name, location = address_database.get_address(name)
        embed = AddressEmbed(op=op, name=name, location=location)
        view = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='delete', description='Delete an existing address')
    async def delete_command(self, interaction: discord.Interaction, name: str) -> None:
        op = 'delete'
        if not address_database.address_exists(name):
            embed = ErrorEmbed(op=op, reason=f'Failed to delete address *{name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        address_database.delete_address(name)
        embed = AddressEmbed(op=op, name=name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @update_command.autocomplete('old_name')
    @get_command.autocomplete('name')
    @delete_command.autocomplete('name')
    async def autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        if current == '' or self.autocomplete_cache is None:
            self.autocomplete_cache = [address[0] for address in address_database.get_addresses()]
        return [
            app_commands.Choice(name=name, value=name)
            for name in self.autocomplete_cache
            if current.lower() in name.lower()
        ]


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AddressCog())
