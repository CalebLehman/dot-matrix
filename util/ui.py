import discord


class ErrorEmbed(discord.Embed):
    def __init__(self, op: str, reason: str) -> None:
        super().__init__(color=discord.Color.red(), title=f'Error during `/address {op}`', description=reason)


class SuccessEmbed(discord.Embed):
    def __init__(self, op: str, reason: str) -> None:
        self.title = f'Successfully competed `/{op}`'
        super().__init__(color=discord.Color.blurple(), title=self.title, description=reason)
