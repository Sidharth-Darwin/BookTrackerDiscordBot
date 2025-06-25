import discord
from discord.ext import commands
from discord import Member
from config import DEBUG

ENTRY_ROLE_NAME: str = "Reader"
WELCOME_CHANNEL: int = 1382053862231379978

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_log_channel(self):
        return self.bot.get_channel(WELCOME_CHANNEL)

    async def log_to_admins(self, message: str):
        """Send error logs to the admin log channel"""
        channel = self.get_log_channel()
        if channel:
            try:
                await channel.send(f"⚠️ **Bot Error:** {message}")
            except Exception as e:
                if DEBUG:
                    print(f"❌ Failed to log to admin channel: {e}")
        elif DEBUG:
            print(f"⚠️ Admin log channel not found. Error: {message}")

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        log_channel = self.get_log_channel()

        # 1. Welcome Message
        if log_channel:
            try:
                await log_channel.send(
                    f"👋 Welcome to the server, {member.mention}! Check your DMs for the rules. 📜"
                )
            except Exception as e:
                await self.log_to_admins(f"Couldn't send welcome message for {member.mention}: `{e}`")
        elif DEBUG:
            print("⚠️ Welcome channel not found.")

        # 2. Auto-assign Reader Role
        role = discord.utils.get(member.guild.roles, name=ENTRY_ROLE_NAME)
        if role:
            try:
                await member.add_roles(role, reason="Auto-assigned on join")
                if DEBUG:
                    print(f"✅ Assigned 'Reader' role to {member}")
            except Exception as e:
                await self.log_to_admins(f"Couldn't assign 'Reader' role to {member.mention}: `{e}`")
        else:
            await self.log_to_admins(f"Role '{ENTRY_ROLE_NAME}' not found in the guild.")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))