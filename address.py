from typing import Optional
from urllib.parse import quote_plus

from discord import app_commands, ButtonStyle, Color, Embed, File, Interaction
from discord.app_commands import Choice
from discord.ext.commands import Bot, GroupCog
from discord.ui import Button, View

from database import Database


class ErrorEmbed(Embed):
    def __init__(self, op: str, reason: str) -> None:
        super().__init__(color=Color.red(), title=f'Error during `/address {op}`', description=reason)


class AddressEmbed(Embed):
    def __init__(self, op: str, name: str, location: Optional[str] = None) -> None:
        title = f'Successfully competed `/address {op}`'
        color = Color.blurple()
        if location is not None:
            description = f'''
>>> **{name}**
{location}
'''
            super().__init__(color=color, title=title, description=description)
        else:
            super().__init__(color=color, title=title)


class AddressView(View):
    def __init__(self, location: str) -> None:
        super().__init__()
        self.add_item(Button(
            label='Google Maps',
            url=f'https://www.google.com/maps/search/?api=1&query={quote_plus(location)}',
            style=ButtonStyle.link,
        ))


class AddressCog(GroupCog, name='address'):
    def __init__(self) -> None:
        self.database = Database()
        self.autocomplete_cache = None
        super().__init__()

    @app_commands.command(name='about', description='Information about the `address` group')
    async def about_command(self, interaction: Interaction) -> None:
        description = '''
A group of commands for managing a **collection of addresses**. \
The **goal** is to eliminate the need for all *what was your address again?*-type questions in the chat. \
To see the available commands, type `/address` and look through the autocomplete options.
'''
        embed = Embed(title='About `address`', description=description)
        embed.set_image(url='attachment://address_about.png')
        file = File('assets/address_about.png')
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)

    @app_commands.command(name='set', description='Set a new address')
    async def set_command(self, interaction: Interaction, name: str, location: str) -> None:
        op = 'set'
        if self.database.address_exists(name):
            embed: Embed = ErrorEmbed(op=op, reason=f'Failed to set new address *{name}* (already exists)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.database.create_address(name, location)
        name, location = self.database.get_address(name)
        embed: Embed = AddressEmbed(op=op, name=name, location=location)
        view: View = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='update', description='Update an existing addres')
    async def update_command(
        self,
        interaction: Interaction,
        old_name: str,
        new_name: Optional[str],
        new_location: Optional[str],
    ) -> None:
        op = 'update'
        new_name = new_name or old_name
        if not self.database.address_exists(old_name):
            embed: Embed = ErrorEmbed(op=op, reason=f'Failed to update address *{old_name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if new_name is not None and new_name.lower() != old_name.lower() and self.database.address_exists(new_name):
            embed: Embed = ErrorEmbed(
                op=op,
                reason=f'Failed to update address *{old_name}* to *{new_name}* (already exists)',
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if new_name is None and new_location is None:
            embed: Embed = ErrorEmbed(op=op, reason='Failed to update because no updates were provided')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.database.update_address(old_name, new_name, new_location)
        name: str
        location: str
        name, location = self.database.get_address(new_name)
        embed: Embed = AddressEmbed(op=op, name=name, location=location)
        view: View = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='get', description='Get an existing address')
    async def get_command(self, interaction: Interaction, name: str) -> None:
        op = 'get'
        if not self.database.address_exists(name):
            embed: Embed = ErrorEmbed(op=op, reason=f'Failed to get address *{name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        location: str
        name, location = self.database.get_address(name)
        embed: Embed = AddressEmbed(op=op, name=name, location=location)
        view: View = AddressView(location=location)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='delete', description='Delete an existing address')
    async def delete_command(self, interaction: Interaction, name: str) -> None:
        op = 'delete'
        if not self.database.address_exists(name):
            embed: Embed = ErrorEmbed(op=op, reason=f'Failed to delete address *{name}* (does not exist)')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        self.database.delete_address(name)
        embed: Embed = AddressEmbed(op=op, name=name)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @update_command.autocomplete('old_name')
    @get_command.autocomplete('name')
    @delete_command.autocomplete('name')
    async def autocomplete(self, interaction: Interaction, current: str) -> list[Choice[str]]:
        if current == '' or self.autocomplete_cache is None:
            self.autocomplete_cache = [address[0] for address in self.database.get_addresses()]
        return [Choice(name=name, value=name) for name in self.autocomplete_cache if current.lower() in name.lower()]


async def setup(bot: Bot) -> None:
    await bot.add_cog(AddressCog())
