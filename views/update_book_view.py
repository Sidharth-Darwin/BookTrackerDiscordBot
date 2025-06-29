import discord
from discord import ui, Interaction
from utils.excel import read_excel_async
from config import EXCEL_FILE
from modals.update_book_modal import UpdateBookModal


class UpdateBookSelectView(ui.View):
    """
    A Discord UI View that presents a dropdown menu for users to select one of their books to update.

    Args:
        user_books (list[str]): A list of book titles associated with the user.

    Attributes:
        select (ui.Select): The dropdown select menu populated with up to 25 unique book titles.

    Methods:
        on_select(interaction: Interaction):
            Callback triggered when a user selects a book from the dropdown.
            Opens an UpdateBookModal pre-filled with the selected book's details.

        _get_book(interaction: Interaction):
            Asynchronously retrieves the selected book's details for the current user from the Excel file.
            Returns a dictionary of book attributes, or default values if the book is not found.
    """
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        user_books = list(set(user_books))[:25]  # Limit to 25 unique books for the select menu
        self.select = ui.Select(
            placeholder="Select a book to update",
            options=[discord.SelectOption(label=title.title(), value=title) for title in user_books]
        )
        self.select.callback = self.on_select
        self.add_item(self.select)

    async def on_select(self, interaction: Interaction):
        await interaction.response.send_modal(UpdateBookModal(await self._get_book(interaction)))

    async def _get_book(self, interaction: Interaction):
        df = await read_excel_async(EXCEL_FILE)
        df["UserID"] = df["UserID"].astype(str)
        selected_book = self.select.values[0]
        book_row = df[
            (df["UserID"] == str(interaction.user.id)) &
            (df["BookName"].str.lower() == selected_book.lower())
        ]
        if book_row.empty:
            # Modal can't be cancelled, so send a followup error after modal closes
            # But this should not happen as select options are from user's books
            return {
                "BookName": selected_book,
                "Author": "",
                "Genres": "",
                "LastPage": 0,
                "TotalPages": 0
            }
        return book_row.iloc[0].to_dict()
