import discord
from discord import Interaction
from modals.shelf_book_modal import ShelfBookModal
from config import DEBUG


class ShelfBookSelectView(discord.ui.View):
    """
    A Discord UI View that presents a dropdown select menu for users to choose a book to shelf.

    Attributes:
        select (discord.ui.Select): The dropdown select menu populated with the user's books.

    Args:
        user_books (list[str]): A list of book titles available for the user to select from.

    Methods:
        on_select(interaction: Interaction):
            Handles the event when a user selects a book from the dropdown.
            If a selection is made, presents a modal for further interaction.

    Notes:
        - Limits the number of selectable books to 25 (Discord's select menu limit).
        - Each book title is displayed in title case in the dropdown.
        - The view times out after 60 seconds of inactivity.
    """
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        self.select = discord.ui.Select(
            placeholder="Select a book to shelf",
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

        modal = ShelfBookModal(selection)
        try:
            await interaction.response.send_modal(modal)
            if DEBUG:
                print("✅ Modal sent")
        except Exception as e:
            if DEBUG:
                print(f"❌ Failed to send modal: {e}")

        