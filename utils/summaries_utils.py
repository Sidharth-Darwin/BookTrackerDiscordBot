from datetime import datetime, timedelta
import discord
from config import GUILD_ID

def get_week_bounds(reference: datetime):
    start_of_week = reference - timedelta(days=reference.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week, end_of_week

async def get_user_mentions(user_ids: list[int], bot) -> list[str]:
    mentions = []
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print(f"⚠️ Guild with ID {GUILD_ID} not found.")
        return mentions
    for uid in user_ids:
        try:
            member = guild.get_member(uid) or await guild.fetch_member(uid)
            if member:
                mentions.append(member.mention)
        except discord.NotFound:
            print(f"⚠️ Member with ID {uid} not found in guild.")
        except Exception as e:
            print(f"⚠️ Error fetching member {uid}: {e}")
    return mentions

def get_all_reader_ids(guild: discord.Guild) -> list[str]:
    reader_role = discord.utils.get(guild.roles, name="Reader")
    bot_role = discord.utils.get(guild.roles, name="Bots")
    if not reader_role:
        print("⚠️ 'Reader' role not found in guild.")
        return []
    return [
        str(member.id)
        for member in guild.members
        if reader_role in member.roles and (not bot_role or bot_role not in member.roles) and not member.bot
    ]
