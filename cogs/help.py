from discord.ext import commands
from discord import app_commands, Interaction
import discord
from config import GUILD_ID, DATE_CUTOFF_DAYS


class HelpCog(commands.Cog):
    """
    HelpCog provides a set of commands to assist users in navigating and utilizing the BookTrackerBot.

    This cog includes:
    - A slash command `/help` that displays an embedded help message listing all available commands, grouped by category (General, Progress Reports, Admin).
    - Descriptions for each command, including usage notes and admin-only restrictions.
    - Dynamic inclusion of configurable values such as `DATE_CUTOFF_DAYS` for progress reports.
    - The help message is visible only to the user who invoked the command.

    Args:
        bot (commands.Bot): The Discord bot instance to which this cog is attached.

    Attributes:
        bot (commands.Bot): Reference to the bot instance.

    Commands:
        /help: Sends an embedded help message with categorized command listings and descriptions.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get help with the bot commands")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def help_command(self, interaction: Interaction):
        embed = discord.Embed(
            title="📚 BookTrackerBot Help",
            description="Here are the available commands:",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="📘 General Commands",
            value=(
                "`/add_book` — Add a new book to your reading list.\n"
                "`/update_book` — Update your reading progress.\n"
                "`/shelf_book` — Mark a book as shelved (completed/paused).\n"
                "`/unshelf_book` — Return a shelved book to reading status.\n"
                "`/delete_book` — Permanently delete a book from your log.\n"
                "`/genres` — List all available genres.\n"
                "`/help` — Show this help message."
            ),
            inline=False
        )

        embed.add_field(
            name="📊 Progress Reports",
            value=(
                f"`/progress` — See your own progress (last {DATE_CUTOFF_DAYS} days).\n"
                f"`/progress @user1 @user2 ...` — See progress of mentioned users (last {DATE_CUTOFF_DAYS} days).\n"
                f"`/progress *` — See everyone's progress (Admins only) (last {DATE_CUTOFF_DAYS} days)."
            ),
            inline=False
        )

        embed.add_field(
            name="🗂️ Log Commands",
            value=(
                "`/download_log [user]` — Download your own reading log as an Excel file. Admins can specify a user to download their log.\n"
                "`/download_log_all` — Download the full reading log (Admins only, restricted to log channel).\n"
                "`/gsheet_sync` — Manually sync Excel to Google Sheet."
            ),
            inline=False
        )

        embed.set_footer(text="Note: Admin-only commands are only visible or executable by users with admin permissions.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
