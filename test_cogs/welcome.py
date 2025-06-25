import io
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import discord
from discord.ext import commands
from discord import Member
from config import DEBUG

ENTRY_ROLE_NAME = "Reader"
WELCOME_CHANNEL_ID = 1382053862231379978
TEMPLATE_PATH = "resources/template.jpeg"
FONT_PATH = "resources/DejaVuSans-Bold.ttf"

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load template once
        self.template = Image.open(TEMPLATE_PATH).convert("RGBA")
        self.font_large = ImageFont.truetype(FONT_PATH, 50)
        self.font_small = ImageFont.truetype(FONT_PATH, 45)

    def get_welcome_channel(self):
        return self.bot.get_channel(WELCOME_CHANNEL_ID)

    async def generate_welcome_image(self, member: discord.Member) -> discord.File:
        base = self.template.copy()
        draw = ImageDraw.Draw(base)

        # === Avatar Settings ===
        avatar_asset = member.display_avatar.with_format("png").with_size(512)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar_asset.url)) as resp:
                avatar_bytes = await resp.read()
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
        avatar_size = 360
        avatar = avatar.resize((avatar_size, avatar_size))

        # Circular mask
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, avatar_size, avatar_size), fill=255)
        avatar.putalpha(mask)

        # Position avatar
        avatar_x = 100
        avatar_y = 200
        base.paste(avatar, (avatar_x, avatar_y), avatar)

        # === Text Content ===
        top_text = "Whoa!\nA new reader arrived! ❤️"
        bottom_text = f"Welcome {member.display_name}!\nMake yourself at home."

        # === Text Bounding Boxes (optional use for debugging layout)
        top_bbox = draw.textbbox((0, 0), top_text, font=self.font_large)
        bottom_bbox = draw.textbbox((0, 0), bottom_text, font=self.font_small)


        top_text_x = 70 
        top_text_y = 50 
        bottom_text_x = 70 
        bottom_text_y = 600 

        # === Draw Text ===
        draw.text((top_text_x, top_text_y), top_text, font=self.font_large, fill="black")
        draw.text((bottom_text_x, bottom_text_y), bottom_text, font=self.font_small, fill="black")

        # === Return as Discord File ===
        buffer = io.BytesIO()
        base.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename="welcome.png")




    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        channel = self.get_welcome_channel()

        # Send welcome image or fallback text
        if channel:
            try:
                file = await self.generate_welcome_image(member)
                await channel.send(file=file)
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Image gen failed: {e}")
                # Fallback message without attempting to resend image
                await channel.send(
                    f"Whoa! A new reader arrived! ❤️\n"
                    f"Welcome {member.mention}! Make yourself at home."
                )
        elif DEBUG:
            print("⚠️ Welcome channel not found.")

        # Assign 'Reader' role
        role = discord.utils.get(member.guild.roles, name=ENTRY_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role, reason="Auto-assigned on join")
                if DEBUG:
                    print(f"✅ Assigned '{ENTRY_ROLE_NAME}' to {member.display_name}")
            except Exception as e:
                if DEBUG:
                    print(f"❌ Failed to assign role: {e}")
        elif DEBUG:
            print(f"⚠️ Role '{ENTRY_ROLE_NAME}' not found in guild.")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
