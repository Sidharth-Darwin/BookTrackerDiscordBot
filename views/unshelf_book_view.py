from datetime import datetime
import discord
from discord import Interaction
from utils.excel import read_excel_async, write_excel_async
from config import EXCEL_FILE, DEBUG


class UnShelfBookSelectView(discord.ui.View):
    """
    UnShelfBookSelectView is a Discord UI View that presents a dropdown menu for users to select a book to "un-shelf" (resume reading) from their personal reading log.

    Args:
        user_books (list[str]): A list of book titles associated with the user.

    Attributes:
        select (discord.ui.Select): Dropdown menu populated with up to 25 book titles.

    Methods:
        on_select(interaction: Interaction):
            Handles the user's selection from the dropdown. If a valid book is selected, updates the reading log in the Excel file to mark the book as resumed (Status=1) and updates the last modified timestamp. Provides feedback to the user via Discord messages.

    Notes:
        - Only up to 25 book titles are shown due to Discord UI limitations.
        - Requires asynchronous Excel read/write helpers (`read_excel_async`, `write_excel_async`) and a defined `EXCEL_FILE` path.
        - Uses a DEBUG flag for optional error and status logging.
    """
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        self.select = discord.ui.Select(
            placeholder="Select a book to un-shelf",
            options=[discord.SelectOption(label=title.title(), value=title) for title in user_books]
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: Interaction):
        selection = self.select.values[0]

        if not selection:
            if DEBUG:
                print("🟡 No selection made")
            return

        try:
            await interaction.response.defer()  # Allow public followup

            df = await read_excel_async(EXCEL_FILE)
            df["UserID"] = df["UserID"].astype(str)

            match = (
                (df["UserID"] == str(interaction.user.id)) &
                (df["BookName"].str.lower() == selection.lower())
            )

            if not match.any():
                await interaction.followup.send(
                    "⚠️ Book not found in your reading log. Use `/add_book` first.",
                    ephemeral=True
                )
                return

            df.loc[match, ["Status", "LastUpdated"]] = [1, datetime.now()]
            await write_excel_async(df, EXCEL_FILE)

            await interaction.followup.send(
                f"📖 <@{interaction.user.id}> resumed reading **{selection}**.",
                ephemeral=False
            )

        except Exception as e:
            if DEBUG:
                print("❌ Error unshelving:", e)
            await interaction.followup.send(
                f"❌ Something went wrong: {e}",
                ephemeral=True
            )
