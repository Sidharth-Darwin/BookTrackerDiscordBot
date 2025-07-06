from discord.ext import commands, tasks
import discord
from datetime import datetime
import pandas as pd

from config import GUILD_ID, CHANNEL_ID, EXCEL_FILE, DEBUG
from utils.excel import read_excel_async
from utils.summaries_utils import get_week_bounds, get_user_mentions, get_all_reader_ids

class SummaryCog(commands.Cog):
    """
    SummaryCog is a Discord Cog that provides automated daily and weekly summaries and reminders
    for a reading log bot. It schedules three background tasks:
    
    1. daily_summary_loop:
        - Runs every 10 minutes.
        - Posts a summary after 23:50 each day showing who updated logs.
    
    2. weekly_summary_loop:
        - Runs every 10 minutes.
        - Posts a summary after 23:50 every Sunday showing who updated during the week.
    
    3. weekly_reminder_loop:
        - Runs every 10 minutes.
        - At 18:00–18:09 every Sunday, reminds users who haven't updated.
    
    Notes:
    - Uses system time (bot server's local time).
    - All loops are idempotent using a last-run tracker.
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_daily_run = None
        self.last_weekly_summary_run = None
        self.last_weekly_reminder_run = None
        self.daily_summary_loop.start()
        self.weekly_summary_loop.start()
        self.weekly_reminder_loop.start()

    @tasks.loop(minutes=10)
    async def daily_summary_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        today = now.date()

        # Run once daily after 23:50
        if now.hour == 23 and now.minute >= 50:
            if self.last_daily_run == today:
                return
            self.last_daily_run = today

            if DEBUG:
                print(f"📅 Running daily summary for {today} at {now.time()}")

            if not CHANNEL_ID or not GUILD_ID:
                if DEBUG:
                    print("⚠️ CHANNEL_ID or GUILD_ID not set.")
                return

            try:
                df = await read_excel_async(EXCEL_FILE)
                df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
                updated_today = df[df["LastUpdated"].dt.date == today]
                unique_users = updated_today["UserName"].unique().tolist()

                msg = (
                    f"📖 **Daily Reading Log Summary** ({today}):\n"
                    f"{', '.join(f'**{name}**' for name in unique_users)} updated their books today. Great job! 🎉"
                    if unique_users else
                    f"📖 **Daily Reading Log Summary** ({today}):\nNo one has updated their reading progress yet. 😴"
                )

                channel = self.bot.get_channel(CHANNEL_ID)
                if isinstance(channel, discord.TextChannel):
                    await channel.send(msg)
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Error in daily summary task: {e}")

    @tasks.loop(minutes=10)
    async def weekly_summary_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        week_id = now.isocalendar()[1]

        # Run once on Sunday after 23:50
        if now.weekday() == 6 and now.hour == 23 and now.minute >= 50:
            if self.last_weekly_summary_run == week_id:
                return
            self.last_weekly_summary_run = week_id

            if DEBUG:
                print(f"📆 Running weekly summary for week {week_id} at {now.time()}")

            try:
                df = await read_excel_async(EXCEL_FILE)
                df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
                df["UserID"] = df["UserID"].astype(str)

                start_of_week, end_of_week = get_week_bounds(now)
                updated = df[(df["LastUpdated"] >= start_of_week) & (df["LastUpdated"] <= end_of_week)]
                user_ids = updated["UserID"].unique().tolist()

                mentions = await get_user_mentions([int(uid) for uid in user_ids], self.bot)
                msg = (
                    f"📆 Weekly Reading Summary ({start_of_week.date()} → {end_of_week.date()}):\n"
                    f"Great job, {', '.join(mentions)}! 🥳"
                    if mentions else
                    f"📆 Weekly Reading Summary ({start_of_week.date()} → {end_of_week.date()}):\nNo updates this week. 😔"
                )

                channel = self.bot.get_channel(CHANNEL_ID)
                if isinstance(channel, discord.TextChannel):
                    await channel.send(msg)
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Error in weekly_summary_loop: {e}")

    @tasks.loop(minutes=10)
    async def weekly_reminder_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        week_id = now.isocalendar()[1]

        # Run once on Sunday 18:00–18:09
        if now.weekday() == 6 and now.hour == 18 and now.minute < 10:
            if self.last_weekly_reminder_run == week_id:
                return
            self.last_weekly_reminder_run = week_id

            if DEBUG:
                print(f"⏰ Running weekly reminder for week {week_id} at {now.time()}")

            try:
                df = await read_excel_async(EXCEL_FILE)
                df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
                df["UserID"] = df["UserID"].astype(str)

                start_of_week, end_of_week = get_week_bounds(now)
                updated_ids = set(df[(df["LastUpdated"] >= start_of_week) & (df["LastUpdated"] <= end_of_week)]["UserID"])

                guild = self.bot.get_guild(GUILD_ID)
                if not guild:
                    return

                all_ids = set(get_all_reader_ids(guild))
                missing_ids = list(all_ids - updated_ids)

                mentions = await get_user_mentions([int(uid) for uid in missing_ids], self.bot)
                if mentions:
                    msg = (
                        f"⏰ Reminder ({start_of_week.date()} → {end_of_week.date()}):\n"
                        f"{', '.join(mentions)} — you haven’t updated your reading log this week! 📚"
                    )
                    channel = self.bot.get_channel(CHANNEL_ID)
                    if isinstance(channel, discord.TextChannel):
                        await channel.send(msg)
            except Exception as e:
                if DEBUG:
                    print(f"⚠️ Error in weekly_reminder_loop: {e}")

async def setup(bot):
    await bot.add_cog(SummaryCog(bot))
