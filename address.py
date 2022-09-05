from discord import app_commands, Interaction
from discord.ext import commands

from database import Database


class AddressCog(commands.GroupCog, name='address'):
    def __init__(self) -> None:
        self.database = Database()
        super().__init__()

    @app_commands.command(name='set')
    async def set_command(self, interaction: Interaction, name: str, location: str) -> None:
        if self.database.address_exists(name):
            await interaction.response.send_message('fail', ephemeral=True)
            return
        self.database.create_address(name, location)
        await interaction.response.send_message('[clickable](https://google.com)', ephemeral=True)

    @app_commands.command(name='update')
    async def update_command(self, interaction: Interaction, old_name: str, new_name: str, new_location: str) -> None:
        if not self.database.address_exists(old_name):
            await interaction.response.send_message('fail', ephemeral=True)
            return
        if self.database.address_exists(new_name):
            await interaction.response.send_message('fail', ephemeral=True)
            return
        self.database.update_address(old_name, new_name, new_location)
        await interaction.response.send_message('success', ephemeral=True)

    @app_commands.command(name='get')
    async def get_command(self, interaction: Interaction, name: str) -> None:
        if not self.database.address_exists(name):
            await interaction.response.send_message('fail', ephemeral=True)
            return
        name, location = self.database.get_address(name)
        await interaction.response.send_message('success', ephemeral=True)

    @app_commands.command(name='delete')
    async def delete_command(self, interaction: Interaction, name: str) -> None:
        if not self.database.address_exists(name):
            await interaction.response.send_message('fail', ephemeral=True)
            return
        self.database.delete_address(name)
        await interaction.response.send_message('success', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AddressCog())
