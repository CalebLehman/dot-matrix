import discord


async def get_bot_channel(guild: discord.Guild, category_name: str, channel_name: str) -> discord.TextChannel:
    category = discord.utils.get(guild.categories, name=category_name)
    channel = discord.utils.get(guild.channels, name=channel_name, category=category)
    if channel is None:
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: discord.PermissionOverwrite(send_messages=True),
            },
            position=100,
        )
    return channel
