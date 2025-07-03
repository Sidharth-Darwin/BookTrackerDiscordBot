from discord import app_commands, Interaction
from discord.ext import commands
import discord
from config import GUILD_ID
from utils.excel import filter_booknames_with_user_status
from views.unshelf_book_view import UnShelfBookSelectView


class UnShelfBookCog(commands.Cog):
    """
    Cog for handling the 'unshelf_book' command in a Discord bot.
    This cog provides functionality for users to un-shelve books that are currently marked as 'Shelved'.
    When the command is invoked, it checks if the user has any books with the 'Shelved' status.
    If books are found, it presents a selection view for the user to choose which book to un-shelve.
    If no books are found or an error occurs, an appropriate message is sent to the user.
    Attributes:
        bot (commands.Bot): The Discord bot instance.
    Methods:
        unshelf_book(interaction: Interaction):
            Slash command handler for un-shelving a book. Presents a selection view if books are available,
            otherwise notifies the user. Handles exceptions gracefully.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unshelf_book", description="Unshelf a book when it's already shelved")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def unshelf_book(self, interaction: Interaction):   
        user_id = str(interaction.user.id)

        try:
            books = await filter_booknames_with_user_status(user_id, status=0)  # Status 0 = Currently shelved
            
            if not books:
                await interaction.response.send_message(
                    "❌ You don't have any books currently marked as 'Shelved'.", ephemeral=True
                )
                return
            
            await interaction.response.send_message(
                "📚 Select a book you want to un-shelf:", 
                view=UnShelfBookSelectView(books[:25]), 
                ephemeral=False
            )

        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error un-shelving book: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnShelfBookCog(bot))
