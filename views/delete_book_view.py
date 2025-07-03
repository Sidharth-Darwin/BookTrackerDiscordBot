import discord
from discord import ui, Interaction
from config import EXCEL_FILE
from utils.excel import read_excel_async, write_excel_async

class DeleteBookSelectView(ui.View):
    """
    A Discord UI View that allows users to select and delete a book from their reading log.

    This view presents a dropdown (Select) menu populated with the user's books. Upon selection,
    the chosen book is deleted from the user's reading log stored in an Excel file. The deletion
    process is irreversible and provides user feedback upon completion.

    Args:
        user_books (list[str]): A list of book titles associated with the user.

    Attributes:
        select (ui.Select): The dropdown menu for selecting a book to delete.

    Methods:
        on_select(interaction: Interaction):
            Handles the selection event, deletes the selected book from the Excel file,
            and sends a confirmation message to the user.
    """
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        self.select = ui.Select(
            placeholder="Select a book to delete. This process is irreversible.",
            options=[discord.SelectOption(label=title.title(), value=title) for title in user_books[:25]]
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        df = await read_excel_async(EXCEL_FILE)
        df["UserID"] = df["UserID"].astype(str)

        selected_value = self.select.values[0]
        is_audiobook = selected_value.startswith("🎧 ")
        selected_book = selected_value[2:] 
        if is_audiobook:
            match = (
                (df["UserID"] == str(interaction.user.id)) &
                (df["BookName"].str.lower() == selected_book.lower()) &
                (df["Genres"].str.contains("audiobook", na=False))
            )
        else:
            match = (
                (df["UserID"] == str(interaction.user.id)) &
                (df["BookName"].str.lower() == selected_book.lower()) &
                (~df["Genres"].str.contains("audiobook", na=False))
            )

        df = df[~match]
        await write_excel_async(df, EXCEL_FILE)

        await interaction.followup.send(
            f"🗑️ **{selected_book.title()}** has been deleted from your reading log.\n"
            "😢 Sometimes, it's okay to let a book go. On to new adventures!",
            ephemeral=False
        )
