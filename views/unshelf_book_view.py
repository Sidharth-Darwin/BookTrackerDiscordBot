from datetime import datetime
import discord
from discord import Interaction
from utils.excel import read_excel_async, write_excel_async
from config import EXCEL_FILE, DEBUG


class UnShelfBookSelectView(discord.ui.View):
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        user_books = list(set(user_books))[:25] 
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
