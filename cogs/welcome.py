from pathlib import Path
import io
import aiohttp
import discord
from discord import Member
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from config import DEBUG, ENTRY_ROLE_NAME, WELCOME_CHANNEL_ID, TEMPLATE_PATH


class WelcomeCog(commands.Cog):
    """
    A Discord Cog that handles welcoming new members to the server.

    Features:
    - Sends a custom welcome image to a designated channel when a member joins.
    - Assigns a predefined entry role to the new member.
    - Sends a direct message to the new member with server rules and bot usage instructions.

    Attributes:
        bot (commands.Bot): The Discord bot instance.
        template (Image): The base image template for welcome images.
        font_large (ImageFont): Font used for large text in the welcome image.
        font_small (ImageFont): Font used for small text in the welcome image.
    """

    def __init__(self, bot):
        self.bot = bot
        # Preload resources for welcome images
        self.template = Image.open(TEMPLATE_PATH).convert("RGBA")
        # Choose a working font (made for linux systems)
        common_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        for path in common_fonts:
            if Path(path).exists():
                try:
                    self.font_large = ImageFont.truetype(path, 50)
                    self.font_small = ImageFont.truetype(path, 45)
                    break
                except Exception:
                    pass
        else:
            self.font_large = self.font_small = ImageFont.load_default()

    def get_welcome_channel(self):
        """
        Returns the Discord channel object for sending welcome messages.
        """
        return self.bot.get_channel(WELCOME_CHANNEL_ID)

    async def generate_welcome_image(self, member: Member) -> discord.File:
        """
        Generates a personalized welcome image for the new member.

        Args:
            member (discord.Member): The new member who joined.

        Returns:
            discord.File: The image file to be sent in the welcome channel.
        """
        base = self.template.copy()
        draw = ImageDraw.Draw(base)

        # Avatar processing
        avatar_asset = member.display_avatar.with_format("png").with_size(512)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_asset.url)) as resp:
                avatar = Image.open(io.BytesIO(await resp.read())).convert("RGBA")
        avatar = avatar.resize((360, 360))
        mask = Image.new("L", avatar.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + avatar.size, fill=255)
        avatar.putalpha(mask)
        base.paste(avatar, (100, 200), avatar)

        # Text overlays
        draw.text((70, 50), "Whoa!\nA new reader arrived! ❤️", font=self.font_large, fill="black")
        draw.text((70, 600), f"Welcome {member.display_name}!\nMake yourself at home.",
                  font=self.font_small, fill="black")

        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="welcome.png")

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        """
        Event listener for when a new member joins the server.

        - Sends a welcome image in the welcome channel.
        - Assigns the entry role to the new member.
        - Sends a DM with rules and bot usage instructions.
        """
        # Send welcome image in server
        channel = self.get_welcome_channel()
        if channel:
            try:
                await channel.send(file=await self.generate_welcome_image(member))
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Image gen failed: {e}")
                await channel.send(f"Whoa! A new reader arrived! ❤️\nWelcome {member.mention}!")

        # Assign Reader role
        role = discord.utils.get(member.guild.roles, name=ENTRY_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role, reason="Auto-assigned on join")
                if DEBUG:
                    print(f"✅ Assigned '{ENTRY_ROLE_NAME}' to {member}")
            except Exception as e:
                if DEBUG:
                    print(f"❌ Failed role assignment: {e}")

        # Send DM with rules and bot usage
        try:
            dm = discord.Embed(
                title="📚 Welcome to the Reading Group!",
                description="Here are the rules and how to use BookTrackerBot:",
                color=discord.Color.teal()
            )
            dm.add_field(
                name="🔷 Core Rules",
                value=(
                    "➤ No belittling — instant ban.\n"
                    "➤ Stay on topic — no spam.\n"
                    "➤ All books welcome except comics/manga/webtoons.\n"
                    "➤ No NSFW content.\n"
                    "➤ Post a summary + rating when done."
                ),
                inline=False
            )
            dm.add_field(
                name="🤖 Use BookTrackerBot",
                value=(
                    "`/add_book`, `/update_book`, `/shelf_book`, `/unshelf_book`, `/delete_book`\n"
                    "`/progress` commands to track activity.\n"
                    "`/genres`, `/download_log`, `/gsheet_sync` (admins only)"
                ),
                inline=False
            )
            dm.add_field(
                name="⚠️ Spoiler Policy",
                value=(
                    "❌ No spoilers — kick on sight.\n"
                    "✅ Use `||spoiler||` and include the title.\n"
                    "💬 Spoilers only in spoiler channel."
                ),
                inline=False
            )
            dm.set_footer(text="Let the reading begin! 📖✨")
            await member.send(embed=dm)
        except Exception as e:
            if DEBUG:
                print(f"⚠️ Failed to DM rules: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
