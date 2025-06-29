from datetime import datetime, timedelta
import discord
from config import GUILD_ID

def get_week_bounds(reference: datetime):
    """
    Get the start and end datetime objects for the week containing the given reference date.

    Args:
        reference (datetime): The reference datetime for which to calculate the week bounds.

    Returns:
        tuple: A tuple containing two datetime objects:
            - start_of_week (datetime): The datetime representing the start of the week (Monday, 00:00:00).
            - end_of_week (datetime): The datetime representing the end of the week (Sunday, 23:59:59).

    Example:
        >>> get_week_bounds(datetime(2024, 6, 7, 15, 30))
        (datetime(2024, 6, 3, 0, 0), datetime(2024, 6, 9, 23, 59, 59))
    """
    start_of_week = reference - timedelta(days=reference.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week, end_of_week

async def get_user_mentions(user_ids: list[int], bot) -> list[str]:
    """
    Asynchronously retrieves Discord mention strings for a list of user IDs in a specific guild.

    Args:
        user_ids (list[int]): A list of Discord user IDs to fetch mentions for.
        bot: The Discord bot instance, expected to have `get_guild` and `fetch_member` methods.

    Returns:
        list[str]: A list of mention strings (e.g., '<@user_id>') for the users found in the guild.

    Notes:
        - If the guild with the specified GUILD_ID is not found, an empty list is returned.
        - If a user is not found in the guild, a warning is printed and that user is skipped.
        - Handles exceptions for missing members and other errors during fetching.
    """
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
    """
    Retrieve the IDs of all human members in a Discord guild who have the "Reader" role and do not have the "Bots" role.

    Args:
        guild (discord.Guild): The Discord guild (server) to search for members.

    Returns:
        list[str]: A list of member IDs (as strings) who have the "Reader" role, do not have the "Bots" role, and are not bots.

    Notes:
        - If the "Reader" role is not found in the guild, an empty list is returned and a warning is printed.
        - Members who are bots or have the "Bots" role are excluded from the result.
    """
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
