# modals/add_book_modal.py

from discord import ui, Interaction
from datetime import datetime
import pandas as pd

from utils.excel import read_excel_async, write_excel_async, filter_booknames_with_user_status
from utils.genres import GENRE_LIST
from config import EXCEL_FILE, GUILD_ID


class AddBookModal(ui.Modal):
    """A Discord UI Modal for adding a new book to the user's reading list.

    This modal collects information about a book, including its name, author(s), genres,
    last page read, and total pages. It validates the input, checks for duplicate entries,
    and updates the Excel database accordingly. If the user has reached the maximum number
    of active books, the they are asked to shelve some books. If invalid data is provided, 
    appropriate feedback is sent.

    Attributes:
        bookname (ui.TextInput): The name of the book.
        author (ui.TextInput): The author(s) of the book, comma-separated.
        genres (ui.TextInput): The genres of the book, comma-separated.
        lastpage (ui.TextInput): The last page read by the user.
        totalpages (ui.TextInput): The total number of pages in the book.
    """

    def __init__(self):
        super().__init__(title="📚 Add a new book")
        self.bookname = ui.TextInput(
            label="Book Name",
            placeholder="e.g. Good Omens",
            required=True,
            max_length=150,
            row=0
        )
        self.author = ui.TextInput(
            label="Author(s) (Comma-separated)",
            placeholder="e.g. Neil Gaiman, Terry Pratchett",
            required=True,
            max_length=100,
            row=1
        )
        self.genres = ui.TextInput(
            label="Genres (comma-separated)",
            placeholder=", ".join(GENRE_LIST[:5]) + ", ...",
            required=True,
            max_length=200,
            row=2
        )
        self.lastpage = ui.TextInput(
            label="Last Page Read",
            placeholder="e.g. 120",
            default="0",
            required=True,
            max_length=10,
            row=3
        )
        self.totalpages = ui.TextInput(
            label="Total Pages",
            placeholder="e.g. 300",
            required=True,
            max_length=10,
            row=4
        )
        self.add_item(self.bookname)
        self.add_item(self.author)
        self.add_item(self.genres)
        self.add_item(self.lastpage)
        self.add_item(self.totalpages)

    async def on_submit(self, interaction: Interaction):
        """Handles the submission of the modal.

        Validates the input, checks for duplicate books, and writes the new book entry
        to the Excel file. Sends feedback to the user based on the outcome.
        """
        await interaction.response.defer(ephemeral=True)

        if not interaction.guild or interaction.guild.id != GUILD_ID:
            await interaction.followup.send("This is not the allowed server.", ephemeral=True)
            return
        
        user_books = await filter_booknames_with_user_status(str(interaction.user.id), 1)
        if len(user_books) >= 25:
            await interaction.followup.send(
                "⚠️ You have reached the limit of 25 active books. Please shelve some books using `/shelf_book` before adding new ones.",
                ephemeral=True
            )
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
        
        finished_reading: bool = int(self.lastpage.value.strip()) == int(self.totalpages.value.strip())

        if finished_reading:
            new_entry = {
                "Date": datetime.now(),
                "UserID": str(interaction.user.id),
                "UserName": interaction.user.name,
                "BookName": self.bookname.value.strip().lower(),
                "Author": self.author.value.strip().lower(),
                "Genres": ", ".join(genre_values),
                "LastPage": last_page,
                "TotalPages": total_pages,
                "LastUpdated": datetime.now(),
                "Status": 2
            }
        else:
            new_entry = {
                "Date": datetime.now(),
                "UserID": str(interaction.user.id),
                "UserName": interaction.user.name,
                "BookName": self.bookname.value.strip().lower(),
                "Author": self.author.value.strip().lower(),
                "Genres": ", ".join(genre_values),
                "LastPage": last_page,
                "TotalPages": total_pages,
                "LastUpdated": datetime.now(),
                "Status": 1
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
            if finished_reading:
                await interaction.followup.send(
                    f"🏆 **{interaction.user.mention}**, you finished reading **{self.bookname.value.title()}**! 🎉\n"
                    "Amazing job! Time to pick your next adventure. 📚",
                    ephemeral=False
                )
