import discord
from discord import app_commands, Interaction
from discord.ext import commands
from config import EXCEL_FILE, GUILD_ID, LOG_CHANNEL_ID
from utils.excel import read_excel_async
import os
import pandas as pd
from io import BytesIO

class DownloadLogCog(commands.Cog):
    """
    Cog providing commands for downloading user-specific or full reading logs as Excel files.

    Commands:
        /download_log [user]: Download your own reading log or, if admin, another user's log.
        /download_log_all: Download the full reading log (admin only, restricted to log channel).
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="download_log",
        description="📁 Download your own reading log or someone else's (admin only)"
    )
    @app_commands.describe(user="Defaults to yourself. Admins can use this to fetch others' logs.")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def download_log(self, interaction: Interaction, user: discord.User = None):
        """
        Slash command for downloading logs.

        If the invoker uses `/download_log` then it will give them their log as a xlsx file. 
        If the invoker is an admin and they use `/download_log @user` then it will give them 
        the log of the @user as a xlsx file.
        """
        await interaction.response.defer(ephemeral=True)

        target_user = user or interaction.user
        is_admin = interaction.user.guild_permissions.administrator

        if user and not is_admin:
            await interaction.followup.send("⛔ Only admins can download logs for other users.", ephemeral=True)
            return

        if not os.path.exists(EXCEL_FILE):
            await interaction.followup.send("❌ Log file not found.", ephemeral=True)
            return

        try:
            df = await read_excel_async()
            df["UserID"] = df["UserID"].astype(str)
            filtered = df[df["UserID"] == str(target_user.id)]

            if filtered.empty:
                await interaction.followup.send(
                    f"📭 No entries found for {target_user.display_name}.",
                    ephemeral=True
                )
                return

            buffer = BytesIO()
            filtered.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            await interaction.followup.send(
                content=f"📤 Here's the reading log for **{target_user.display_name}**:",
                file=discord.File(buffer, filename=f"{target_user.display_name}_log.xlsx"),
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(
        name="download_log_all",
        description="📁 Download the full reading log (admin only, restricted to log channel)"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def download_log_all(self, interaction: Interaction):
        """
        Slash command for downloading complete logs.

        Useable only if the invoker is an admin. It copies the excel file and then sends it 
        as xlsx file.
        """
        if str(interaction.channel.id) != str(LOG_CHANNEL_ID):
            await interaction.response.send_message(
                f"⛔ This command can only be used in <#{LOG_CHANNEL_ID}>.",
                ephemeral=True
            )
            return

        if not os.path.exists(EXCEL_FILE):
            await interaction.response.send_message("❌ Log file not found.", ephemeral=True)
            return

        try:
            df = await read_excel_async()
            buffer = BytesIO()
            df.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            await interaction.response.send_message(
                content="📤 Here's the full reading log:",
                file=discord.File(buffer, filename="Reading_Log_All.xlsx"),
                ephemeral=False
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    async def cog_app_command_error(self, interaction: Interaction, error):
        if interaction.command and interaction.command.name == "download_log_all":
            if isinstance(error, app_commands.errors.MissingPermissions):
                await interaction.response.send_message("❌ Only administrators can use this command.", ephemeral=True)
            else:
                await interaction.response.send_message(f"❌ Unexpected error: {error}", ephemeral=True)
        else:
            raise error

async def setup(bot):
    await bot.add_cog(DownloadLogCog(bot))
