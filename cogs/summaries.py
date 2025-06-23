from discord.ext import commands, tasks
import discord
from datetime import datetime
import pandas as pd

from config import GUILD_ID, CHANNEL_ID, EXCEL_FILE, DEBUG
from utils.excel import read_excel_async
from utils.summaries_utils import get_week_bounds, get_user_mentions, get_all_reader_ids

class SummaryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_summary_loop.start()
        self.weekly_summary_loop.start()
        self.weekly_reminder_loop.start()

    @tasks.loop(hours=24)
    async def daily_summary_loop(self):
        await self.bot.wait_until_ready()
        if not CHANNEL_ID or not GUILD_ID:
            if DEBUG:
                print("⚠️ CHANNEL_ID or GUILD_ID not set.")
            return

        try:
            df = await read_excel_async(EXCEL_FILE)
            df["LastUpdated"] = pd.to_datetime(df["LastUpdated"])
            today = datetime.now().date()
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

    @tasks.loop(hours=24)
    async def weekly_summary_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.weekday() != 6 or now.hour != 12 or now.minute != 59:
            return

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

    @tasks.loop(hours=24)
    async def weekly_reminder_loop(self):
        await self.bot.wait_until_ready()
        now = datetime.now()
        if now.weekday() != 6 or now.hour != 18:
            return

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
