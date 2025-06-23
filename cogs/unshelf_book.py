from discord import app_commands, Interaction
from discord.ext import commands
import discord
from config import GUILD_ID
from utils.excel import filter_booknames_with_user_status
from views.unshelf_book_view import UnShelfBookSelectView


class UnShelfBookCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unshelf_book", description="Unshelf a book when it's already shelved")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def unshelf_book(self, interaction: Interaction):   
        user_id = str(interaction.user.id)

        try:
            books = await filter_booknames_with_user_status(user_id, status=0)  # Status 0 = Currently shelved
            
            if not books:
                await interaction.response.send_message(
                    "❌ You don't have any books currently marked as 'Shelved'.", ephemeral=True
                )
                return
            
            await interaction.response.send_message(
                "📚 Select a book you want to un-shelf:", 
                view=UnShelfBookSelectView(books), 
                ephemeral=False
            )

        except Exception as e:
            await interaction.response.send_message(f"⚠️ Error un-shelving book: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnShelfBookCog(bot))
