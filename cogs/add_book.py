import discord
from discord.ext import commands
from discord import app_commands, Interaction
from modals.add_book_modal import AddBookModal, AddAudioBookModal
import config

class AddBookCog(commands.Cog):
    """Cog for handling the addition of new books via a Discord slash command."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_book", description="Add a new book.")
    @app_commands.guilds(discord.Object(id=config.GUILD_ID))
    async def add_book(self, interaction: Interaction):
        await interaction.response.send_modal(AddBookModal())
    
    # I can add new commands like this right? 
    @app_commands.command(name="add_audiobook", description="Add a new audiobook.")
    @app_commands.guilds(discord.Object(id=config.GUILD_ID))
    async def add_audiobook(self, interaction: Interaction):
        await interaction.response.send_modal(AddAudioBookModal())

async def setup(bot):
    await bot.add_cog(AddBookCog(bot))
