from discord.ext import commands, tasks
from discord import app_commands, Interaction
import discord
from datetime import datetime

from config import GUILD_ID, LOG_CHANNEL_ID, DEBUG
from utils.google_sync import sync_excel_to_google_sheet

class GoogleSyncCog(commands.Cog):
    """
    Cog for syncing Excel data to Google Sheets, both automatically and via a manual command.
    """

    def __init__(self, bot):
        self.bot = bot
        self.weekly_google_sync.start()

    @tasks.loop(hours=1)
    async def weekly_google_sync(self):
        """
        Automatically syncs Excel data to Google Sheets every Sunday at 11:00 AM.
        """
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.weekday() == 6 and now.hour == 11:
            try:
                if DEBUG:
                    print("📤 Auto-sync to Google Sheet starting...")
                success, warning = await sync_excel_to_google_sheet()
                if DEBUG:
                    if success:
                        print("✅ Auto-sync completed successfully.")
                    if warning:
                        print(warning)
            except Exception as e:
                if DEBUG:
                    print(f"❌ Auto-sync failed: {e}")

    @app_commands.command(
        name="gsheet_sync",
        description="Sync Excel data and genres to Google Sheet & CSV"
    )
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    @app_commands.checks.has_permissions(administrator=True)
    async def manual_sync(self, interaction: Interaction):
        """
        Manually syncs Excel data to Google Sheets. 
        
        Only available to administrators in the admin channel (LOG_CHANNEL_ID).
        """
        if interaction.channel_id != LOG_CHANNEL_ID:
            await interaction.response.send_message(
                "⛔ This command can only be used in the admin channel.",
                ephemeral=True
            )
            return

        try:
            await interaction.response.defer(ephemeral=True)
            success, warning = await sync_excel_to_google_sheet()
            if success:
                msg = "✅ Excel synced to Google Sheet."
                if warning:
                    msg += f"\n{warning}"
                else:
                    msg += "\n✅ Genres synced to local CSV."
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.followup.send("❌ Sync failed.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Sync failed: {e}", ephemeral=True)

    @manual_sync.error
    async def manual_sync_error(self, interaction: Interaction, error):
        """
        Error handler for the manual sync command.
        """
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "❌ Only administrators can use this command.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Unexpected error: {error}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(GoogleSyncCog(bot))