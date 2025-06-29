import discord
from discord.ext import commands
from discord import app_commands, Interaction
from modals.add_book_modal import AddBookModal
import config

class AddBookCog(commands.Cog):
    """Cog for handling the addition of new books via a Discord slash command."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_book", description="Add a new book.")
    @app_commands.guilds(discord.Object(id=config.GUILD_ID))
    async def add_book(self, interaction: Interaction):
        """
        Slash command to prompt the user with a modal for adding a new book.

        Calls the `AddBookModal` instance.
        """
        await interaction.response.send_modal(AddBookModal())

async def setup(bot):
    await bot.add_cog(AddBookCog(bot))
