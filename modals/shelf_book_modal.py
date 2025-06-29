import string
from datetime import datetime
import discord
from discord import Interaction
from config import EXCEL_FILE, DEBUG
from utils.excel import read_excel_async, write_excel_async

class ShelfBookModal(discord.ui.Modal):
    """
    A Discord UI Modal for shelving a book in the user's reading log.
    This modal prompts the user to provide a reason for shelving a selected book.
    Upon submission, it validates the input, updates the book's status in an Excel-based reading log,
    and notifies the user of the successful operation.
    Args:
        book_name (str): The name of the book to be shelved.
    Attributes:
        selected_book (str): The name of the book being shelved.
        reason (discord.ui.TextInput): Text input field for the user to provide a shelving reason.
    Methods:
        on_submit(interaction: Interaction):
            Handles the modal submission event. Validates the reason, updates the reading log,
            and sends feedback to the user. Handles errors gracefully and provides debug output if enabled.
    Raises:
        Sends an ephemeral error message to the user if:
            - No reason is provided.
            - The book is not found in the user's reading log.
            - An unexpected exception occurs during processing.
    """
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
