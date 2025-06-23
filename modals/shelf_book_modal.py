import string
from datetime import datetime
import discord
from discord import Interaction
import pandas as pd
from config import EXCEL_FILE, DEBUG
from utils.excel import read_excel_async, write_excel_async

class ShelfBookModal(discord.ui.Modal):
    def __init__(self, book_name: str):
        super().__init__(title="Shelf Book")
        self.selected_book = book_name

        self.reason = discord.ui.TextInput(
            label=f"Why are you shelving this book?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=300,
            placeholder="E.g., Too dense right now, switching to something else..."
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            
            strip_chars = string.digits + string.whitespace + string.punctuation
            if not self.reason.value.strip(strip_chars):
                if DEBUG:
                    print("⚠️ No reason provided.")
                await interaction.followup.send("⚠️ Please provide a reason.", ephemeral=True)
                return

            df = await read_excel_async(EXCEL_FILE)
            df["UserID"] = df["UserID"].astype(str)

            match = (
                (df["UserID"] == str(interaction.user.id)) &
                (df["BookName"].str.lower() == self.selected_book.lower())
            )

            if not match.any():
                await interaction.followup.send(
                    "⚠️ Book not found in your reading log. Please add it first using `/add_book`.",
                    ephemeral=True
                )
                return

            df.loc[match, ["Status", "LastUpdated"]] = [0, datetime.now()]
            await write_excel_async(df, EXCEL_FILE)

            await interaction.followup.send(
                f"📚 <@{interaction.user.id}> shelved **{self.selected_book}**.\nReason: _{self.reason.value}_",
                ephemeral=False
            )

        except Exception as e:
            if DEBUG:
                print("❌ Error in modal on_submit:", e)
            await interaction.followup.send(
                f"❌ Something went wrong: {e}",
                ephemeral=True
            )
