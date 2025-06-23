import discord
from discord import Interaction
from modals.shelf_book_modal import ShelfBookModal
from config import DEBUG


class ShelfBookSelectView(discord.ui.View):
    def __init__(self, user_books: list[str]):
        super().__init__(timeout=60)
        user_books = list(set(user_books))[:25] 
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

        