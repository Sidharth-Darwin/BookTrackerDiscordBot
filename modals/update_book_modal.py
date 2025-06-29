from datetime import datetime
from discord import ui, Interaction
from utils.excel import read_excel_async, write_excel_async
from config import EXCEL_FILE
from utils.genres import GENRE_LIST



class UpdateBookModal(ui.Modal, title="✏️ Update book progress."):
    """
    UpdateBookModal is a Discord UI modal for updating the progress of a book in a user's reading log.
    Args:
        book (dict): A dictionary containing the book's current details, including "BookName", "Author", "Genres", "LastPage", and "TotalPages".
    Attributes:
        selected_book (str): The name of the book being updated.
        bookname (ui.TextInput): Input field for the book's name.
        author (ui.TextInput): Input field for the book's author(s).
        genres (ui.TextInput): Input field for the book's genres (comma-separated).
        lastpage (ui.TextInput): Input field for the last page read.
        totalpages (ui.TextInput): Input field for the total number of pages.
    Methods:
        on_submit(interaction: Interaction):
            Handles the submission of the modal. Validates user input, checks for valid genres, ensures page numbers are logical, updates the book entry in the Excel file, and sends a confirmation message to the user. If the book is finished, updates the status accordingly and sends a congratulatory message.
    Raises:
        ValueError: If the last page or total pages are not valid integers.
        ValidationError: If genres are invalid or page numbers are illogical.
    Usage:
        Instantiate with a book dictionary and present to the user for updating their reading progress.
    """
    def __init__(self, book):
        super().__init__()
        self.selected_book = book["BookName"]

        self.bookname = ui.TextInput(label="Book Name", default=book["BookName"], required=True, row=0)
        self.author = ui.TextInput(label="Author(s)", default=book["Author"], required=True, row=1)
        self.genres = ui.TextInput(
            label="Genres (Comma-separated)",
            default=book["Genres"],
            required=True,
            row=2
        )
        self.lastpage = ui.TextInput(label="Last Page Read", default=str(book["LastPage"]), required=True, row=3)
        self.totalpages = ui.TextInput(label="Total Pages", default=str(book["TotalPages"]), required=True, row=4)

        self.add_item(self.bookname)
        self.add_item(self.author)
        self.add_item(self.genres)
        self.add_item(self.lastpage)
        self.add_item(self.totalpages)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

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
        
        genre_values = [genre.strip().lower() for genre in set(self.genres.value.split(","))]
        invalid_genres = [genre for genre in genre_values if genre not in GENRE_LIST]

        if invalid_genres:
            await interaction.followup.send(
                f"⚠️ Invalid genres found: {', '.join(invalid_genres)}. Please use genres from the provided list. Use `/genres` to see the list.",
                ephemeral=True
            )
            return
        
        try:
            last_page = int(self.lastpage.value.strip())
            total_pages = int(self.totalpages.value.strip())
        except ValueError:
            await interaction.followup.send(
                "⚠️ Last page read and total pages must be valid integers.",
                ephemeral=True
            )
            return

        if last_page > total_pages:
            await interaction.followup.send(
                "⚠️ Last page read cannot be greater than total pages.",
                ephemeral=True
            )
            return

        if last_page < 0 or total_pages <= 0:
            await interaction.followup.send(
                "⚠️ Last page read and total pages must be positive integers.",
                ephemeral=True
            )
            return
        
        finished_reading: bool = int(self.lastpage.value.strip()) == int(self.totalpages.value.strip())

        if finished_reading:
            df.loc[match, ["BookName", "Author", "Genres", "LastPage", "TotalPages", "LastUpdated", "Status"]] = [
                self.bookname.value.strip(),
                self.author.value.strip(),
                ", ".join([genre for genre in genre_values]),
                last_page,
                total_pages,
                datetime.now(),
                2
            ]
        else:
            df.loc[match, ["BookName", "Author", "Genres", "LastPage", "TotalPages", "LastUpdated"]] = [
                self.bookname.value.strip(),
                self.author.value.strip(),
                ", ".join([genre for genre in genre_values]),
                last_page,
                total_pages,
                datetime.now()
            ]

        await write_excel_async(df, EXCEL_FILE)

        if finished_reading:
            msg = (
                f"🏆 **{interaction.user.mention}**, you finished reading **{self.bookname.value.title()}**! 🎉\n"
                "Amazing job! Time to pick your next adventure. 📚"
            )
        else:
            percent = (int(self.lastpage.value.strip()) / int(self.totalpages.value.strip())) * 100
            msg = (
                f"✅ **{interaction.user.mention}**, your progress for **{self.bookname.value.title()}** has been updated.\n"
                f"You're {percent:.2f}% done. Keep going!"
            )
        await interaction.followup.send(msg, ephemeral=False)
