from discord.ext import commands
from discord import app_commands, Interaction
import discord

from views.update_book_view import UpdateBookSelectView
from utils.excel import read_excel_async
from config import EXCEL_FILE, GUILD_ID
import pandas as pd

class UpdateBookCog(commands.Cog):
    """
    Cog for updating user progress for a book via a Discord slash command.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update_book", description="Update your progress for a book")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def update_book(self, interaction: Interaction):
        """
        Slash command to update the user's progress for a book.
        Shows a dropdown of active books for the user to select and update.
        """
        try:
            df = await read_excel_async(EXCEL_FILE)
            df["UserID"] = df["UserID"].astype(str)
        except FileNotFoundError:
            await interaction.response.send_message("📁 No books logged yet.", ephemeral=True)
            return

        user_books = df[
            (df["UserID"] == str(interaction.user.id)) &
            (df["LastPage"] != df["TotalPages"])
        ].sort_values(
            by="LastUpdated",
            ascending=False,
            key=lambda x: pd.to_datetime(x, errors='coerce')
        )["BookName"].dropna().tolist()

        if not user_books:
            await interaction.response.send_message(
                "📖 You haven’t added any active books yet.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "📘 Select a book to update:",
            view=UpdateBookSelectView(user_books),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(UpdateBookCog(bot))
