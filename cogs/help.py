from discord.ext import commands
from discord import app_commands, Interaction
import discord
from config import GUILD_ID, DATE_CUTOFF_DAYS

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get help with the bot commands")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def help_command(self, interaction: Interaction):
        embed = discord.Embed(
            title="📚 Reading Log Bot Help",
            description="Here are the commands you can use with this bot:",
            color=discord.Color.blue()
        )
        embed.add_field(name="/add_book", value="Add a new book to your reading log.", inline=False)
        embed.add_field(name="/update_book", value="Update your progress for a book you've added.", inline=False)
        embed.add_field(name="/delete_book", value="Delete a book from your reading log. You can't revert this action.", inline=False)
        embed.add_field(name="/genres", value="View the list of available genres.", inline=False)
        embed.add_field(name="/progress", value=f"View your reading progress privately (last {DATE_CUTOFF_DAYS} days).", inline=False)
        embed.add_field(name="/progress @user1 @user2 ...", value=f"View reading progress for mentioned users publicly (last {DATE_CUTOFF_DAYS} days).", inline=False)
        embed.add_field(name="/progress *", value=f"View reading progress for all users (admins only) publicly (last {DATE_CUTOFF_DAYS} days).", inline=False)
        embed.add_field(name="/help", value="Show this help message.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
