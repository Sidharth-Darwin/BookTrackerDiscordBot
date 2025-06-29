from discord.ext import commands
from discord import app_commands, Interaction
import discord
from config import GUILD_ID, DEBUG
from utils.genres import GENRE_LIST

class GenresCog(commands.Cog):
    """Cog for handling genre-related commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="genres", description="View the list of available genres")
    @app_commands.guilds(discord.Object(id=GUILD_ID))
    async def list_genres(self, interaction: Interaction):
        """
        Sends an embed listing all available genres.

        Useable by everyone. The reply is only visible to the invoker. 
        
        """
        await interaction.response.defer(ephemeral=True)

        genres = sorted([genre.title() for genre in GENRE_LIST])
        if "Documentary" not in genres:
            genres.append("Documentary")
            genres.sort()
        rows = [genres[i:i + 2] for i in range(0, len(genres), 2)]
        table_lines = [" | ".join(f"{g:<20}" for g in row) for row in rows]

        embed = discord.Embed(
            title="📚 Available Genres",
            description="Here is the list of currently supported genres.",
            color=discord.Color.green()
        )

        chunk = ""
        for line in table_lines:
            if len(chunk) + len(line) + 1 > 1024:
                embed.add_field(name="\u200b", value=f"```{chunk}```", inline=False)
                chunk = ""
            chunk += line + "\n"
        if chunk:
            embed.add_field(name="\u200b", value=f"```{chunk}```", inline=False)

        embed.set_footer(text="To request a new genre, tag the admins.")
        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(GenresCog(bot))
