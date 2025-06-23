import discord
from discord import app_commands, Interaction
from discord.ext import commands
from config import EXCEL_FILE, GUILD_ID, LOG_CHANNEL_ID  # <- You must define this in config

import os

class AdminDownloadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="download_log",
        description="📁 Download a copy of the reading log (Admin only)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def download_log(self, interaction: Interaction):
        # Check if command is being used in the right channel
        if not interaction.channel or str(interaction.channel.id) != str(LOG_CHANNEL_ID):
            await interaction.response.send_message(
                f"❌ This command can only be used in <#{LOG_CHANNEL_ID}>.",
                ephemeral=True
            )
            return

        if not os.path.exists(EXCEL_FILE):
            await interaction.response.send_message(
                "❌ Log file not found.",
                ephemeral=True
            )
            return

        # Send file to admin-only channel
        await interaction.response.send_message(
            content="📤 Here is the current reading log:",
            file=discord.File(EXCEL_FILE),
            ephemeral=False
        )


async def setup(bot):
    await bot.add_cog(AdminDownloadCog(bot))
