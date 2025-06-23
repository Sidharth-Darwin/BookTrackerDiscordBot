# modals/add_book_modal.py

from discord import ui, Interaction
from datetime import datetime
import pandas as pd

from utils.excel import read_excel_async, write_excel_async
from utils.genres import GENRE_LIST
from config import EXCEL_FILE, GUILD_ID


class AddBookModal(ui.Modal, title="📚 Add a new book"):
    bookname = ui.TextInput(
        label="Book Name",
        placeholder="e.g. Good Omens",
        required=True,
        max_length=150,
        row=0
    )
    author = ui.TextInput(
        label="Author(s) (Comma-separated)",
        placeholder="e.g. Neil Gaiman, Terry Pratchett",
        required=True,
        max_length=100,
        row=1
    )
    genres = ui.TextInput(
        label="Genres (comma-separated)",
        placeholder=", ".join(GENRE_LIST[:5]) + ", ...",
        required=True,
        max_length=200,
        row=2
    )
    lastpage = ui.TextInput(
        label="Last Page Read",
        placeholder="e.g. 120",
        default="0",
        required=True,
        max_length=10,
        row=3
    )
    totalpages = ui.TextInput(
        label="Total Pages",
        placeholder="e.g. 300",
        required=True,
        max_length=10,
        row=4
    )

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild or interaction.guild.id != GUILD_ID:
            await interaction.followup.send("This is not the allowed server.", ephemeral=True)
            return

        df = await read_excel_async(EXCEL_FILE)
        df["UserID"] = df["UserID"].astype(str)

        genre_values = [g.strip().lower() for g in set(self.genres.value.split(","))]
        invalid_genres = [g for g in genre_values if g not in GENRE_LIST]

        if invalid_genres:
            await interaction.followup.send(
                f"⚠️ Invalid genres: {', '.join(invalid_genres)}. Use `/genres` to see the list.",
                ephemeral=True
            )
            return

        try:
            last_page = int(self.lastpage.value.strip())
            total_pages = int(self.totalpages.value.strip())
        except ValueError:
            await interaction.followup.send(
                "⚠️ Pages must be valid integers.",
                ephemeral=True
            )
            return

        if last_page > total_pages or last_page < 0 or total_pages <= 0:
            await interaction.followup.send(
                "⚠️ Invalid page values.",
                ephemeral=True
            )
            return

        new_entry = {
            "Date": datetime.now(),
            "UserID": str(interaction.user.id),
            "UserName": interaction.user.name,
            "BookName": self.bookname.value.strip().lower(),
            "Author": self.author.value.strip().lower(),
            "Genres": ", ".join(genre_values),
            "LastPage": last_page,
            "TotalPages": total_pages,
            "LastUpdated": datetime.now()
        }

        match = (
            (df["UserID"] == new_entry["UserID"]) &
            (df["BookName"].str.lower() == new_entry["BookName"].lower())
        )
        if match.any():
            await interaction.followup.send(
                f"⚠️ **{self.bookname.value.title()}** already exists. Use `/update_book` to update progress.",
                ephemeral=True
            )
        else:
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            await write_excel_async(df, EXCEL_FILE)
            await interaction.followup.send(
                f"🎉 **{interaction.user.mention}** added **{self.bookname.value.title()}** by *{self.author.value.title()}*! Happy reading! 📚",
                ephemeral=False
            )
