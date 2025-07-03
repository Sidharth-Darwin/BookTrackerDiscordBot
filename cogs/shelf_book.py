from discord import app_commands, Interaction
from discord.ext import commands
import discord
from config import GUILD_ID
from utils.excel import filter_booknames_with_user_status
from views.shelf_book_view import ShelfBookSelectView


class ShelfBookCog(commands.Cog):
    """
    Cog for handling the 'shelf_book' command in a Discord bot.
    
    This cog provides functionality for users to temporarily shelf a book they are currently reading.
    It interacts with the user via a slash command, presenting a selection of books marked as 'Currently Reading'.
    If the user has no such books, an appropriate message is sent. Handles errors gracefully and provides feedback.
    Attributes:
        bot (commands.Bot): The Discord bot instance.
    Methods:
        shelf_book(interaction: Interaction):
            Slash command handler that allows a user to select and shelf a book from their 'Currently Reading' list.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shelf_book", description="Temporarily shelf a book you're reading")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def shelf_book(self, interaction: Interaction):   
        user_id = str(interaction.user.id)

        try:
            books = await filter_booknames_with_user_status(user_id, status=1)  # Status 1 = Currently Reading

            if not books:
                await interaction.response.send_message(
                    "❌ You don't have any books currently marked as 'Reading'.", ephemeral=True
                )
                return
            
            await interaction.response.send_message(
                "📚 Select a book you want to shelf:", 
                view=ShelfBookSelectView(books[:25]), 
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error shelving book: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShelfBookCog(bot))
