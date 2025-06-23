import discord
from discord import app_commands, Interaction
from discord.ext import commands
from typing import Optional
from datetime import datetime, timedelta
import pandas as pd
import re

from config import GUILD_ID, EXCEL_FILE, DATE_CUTOFF_DAYS, MAX_FIELDS
from utils.excel import read_excel_async

class ProgressCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tree = bot.tree

        @self.tree.command(
            name="progress",
            description="View reading progress for tagged users, yourself, or all users (admin only)."
        )
        @app_commands.guilds(discord.Object(id=GUILD_ID))
        @app_commands.describe(users="Users to view progress for (optional, mention users or use * for all)")
        async def progress_command(interaction: Interaction, users: Optional[str] = None):
            await self.handle_progress(interaction, users)

    async def handle_progress(self, interaction: Interaction, users: Optional[str]):
        def is_admin(user: discord.Member) -> bool:
            return user.guild_permissions.administrator

        member = interaction.user
        if not isinstance(member, discord.Member):
            if interaction.guild:
                member = interaction.guild.get_member(interaction.user.id)
            if member is None and interaction.guild:
                member = await interaction.guild.fetch_member(interaction.user.id)

        await interaction.response.defer(ephemeral=False)

        if users and users.strip() == "*":
            if not (isinstance(member, discord.Member) and is_admin(member)):
                await interaction.followup.send("Only admins can view the progress of all users with `/progress *`.", ephemeral=True)
                return
            try:
                df = await read_excel_async(EXCEL_FILE)
                user_ids = df["UserID"].dropna().unique().tolist()
                user_ids = [int(uid) for uid in user_ids]
            except Exception as e:
                await interaction.followup.send(f"⚠️ Error reading data: {e}", ephemeral=False)
                return
            embeds = await self.get_reading_progress(user_ids)
            for embed in embeds:
                await interaction.followup.send(embed=embed, ephemeral=False)
            return

        elif users:
            user_ids = [int(uid) for uid in re.findall(r"<@!?(\d+)>", users)]
            if not user_ids:
                await interaction.followup.send("Please mention at least one user or use `/progress *` (admins only).", ephemeral=True)
                return
            embeds = await self.get_reading_progress(user_ids)
            for embed in embeds:
                await interaction.followup.send(embed=embed, ephemeral=False)
            return

        else:
            embeds = await self.get_reading_progress([interaction.user.id])
            for embed in embeds:
                await interaction.followup.send(embed=embed, ephemeral=True)
            return

    async def get_reading_progress(self, user_ids: list[int]) -> list[discord.Embed]:
        try:
            df = await read_excel_async(EXCEL_FILE)
            df["UserID"] = df["UserID"].astype(str)
            df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
        except Exception as e:
            error_embed = discord.Embed(
                title="Reading Progress",
                description=f"⚠️ Error reading data: {e}",
                color=discord.Color.red()
            )
            return [error_embed]

        cutoff_date = datetime.now() - timedelta(days=DATE_CUTOFF_DAYS)
        df = df[df["LastUpdated"] >= cutoff_date]

        embeds = []
        current_embed = discord.Embed(title="📖 Reading Progress", color=discord.Color.purple())
        field_count = 0
        found_any = False

        for uid in user_ids:
            user_books = df[df["UserID"] == str(uid)].sort_values("LastUpdated", ascending=False)
            user_name = f"User ID: {uid}"
            guild = self.bot.get_guild(GUILD_ID)
            if guild:
                member = guild.get_member(uid)
                if not member:
                    try:
                        member = await guild.fetch_member(uid)
                    except discord.NotFound:
                        member = None
                if member:
                    user_name = member.name

            if user_books.empty:
                if field_count >= MAX_FIELDS:
                    embeds.append(current_embed)
                    current_embed = discord.Embed(title="📖 Reading Progress (contd)", color=discord.Color.purple())
                    field_count = 0
                current_embed.add_field(
                    name=user_name,
                    value="No recent reading progress found (within last 1.5 months).",
                    inline=False
                )
                field_count += 1
                continue

            found_any = True

            for _, row in user_books.iterrows():
                if field_count >= MAX_FIELDS:
                    embeds.append(current_embed)
                    current_embed = discord.Embed(title="📖 Reading Progress (contd)", color=discord.Color.purple())
                    field_count = 0

                book_title = row.get("BookName", "Unknown").title()
                author = row.get("Author", "Unknown").title()
                last_page = row.get("LastPage", "N/A")
                total_pages = row.get("TotalPages", "N/A")
                genres = row.get("Genres", "N/A")
                last_updated = row.get("LastUpdated", "N/A")
                try:
                    progress = f"{last_page}/{total_pages} pages ({(int(last_page) / int(total_pages) * 100):.2f}%)" if int(total_pages) > 0 else "N/A"
                except Exception:
                    progress = "N/A"

                current_embed.add_field(
                    name=f"{user_name}: {book_title} by {author}",
                    value=f"Genres: {genres}\nProgress: {progress}\nLast Updated: {last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated != 'N/A' else 'N/A'}",
                    inline=False
                )
                field_count += 1

        if field_count > 0:
            embeds.append(current_embed)

        if not found_any:
            no_data_embed = discord.Embed(
                title="Reading Progress",
                description="No recent reading progress found for the specified user(s) within the last 1.5 months.",
                color=discord.Color.red()
            )
            return [no_data_embed]

        return embeds

async def setup(bot):
    await bot.add_cog(ProgressCog(bot))
