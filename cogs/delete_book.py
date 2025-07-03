from discord.ext import commands
from discord import app_commands, Interaction
import discord
import pandas as pd
from config import EXCEL_FILE, GUILD_ID
from views.delete_book_view import DeleteBookSelectView
from utils.excel import read_excel_async

class DeleteBookCog(commands.Cog):
    """Cog for handling the deletion of books from a user's reading log."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="delete_book", description="Delete a book from your reading log")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def delete_book(self, interaction: Interaction):
        """
        Slash command to delete a book from the user's reading log.

        Loads the reading log from the Excel file, filters books belonging to the user,
        and presents a selection menu for deletion using `DeleteBookSelectView`. 
        """
        try:
            df = await read_excel_async(EXCEL_FILE)
            df["UserID"] = df["UserID"].astype(str)
        except FileNotFoundError:
            await interaction.response.send_message("No books logged yet.", ephemeral=True)
            return

        filtered_df = df[df["UserID"] == str(interaction.user.id)].sort_values(
            by="LastUpdated",
            ascending=False,
            key=lambda x: pd.to_datetime(x, errors='coerce')
        )
        book_prefixes = filtered_df["Genres"].str.contains("audiobook", case=False, na=False)
        user_books = [
            ("🎧 " if is_audio else "📚 ") + str(book)
            for is_audio, book in zip(book_prefixes, filtered_df["BookName"])
            if pd.notna(book)
        ]

        if not user_books:
            await interaction.response.send_message("You haven't added any books yet.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Select a book to delete:",
            view=DeleteBookSelectView(user_books),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(DeleteBookCog(bot))
