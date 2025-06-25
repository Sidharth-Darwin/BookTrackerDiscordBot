import asyncio
import os
import discord
from discord.ext import commands
from config import TOKEN, GUILD_ID, INTENTS, DEBUG, LOG_CHANNEL_ID

bot = commands.Bot(command_prefix="!", intents=INTENTS)
tree = bot.tree

log_channel = None  # Will hold the log channel object
startup_logs = []  # Initialize here globally

async def send_to_log_channel(messages: list[str]):
    global log_channel
    if not log_channel:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            log_channel = guild.get_channel(LOG_CHANNEL_ID)

    if log_channel and isinstance(log_channel, discord.TextChannel):
        content = "🛠️ **Startup Log:**\n" + "\n".join(messages)
        print(content)
        await log_channel.send(content)
    else:
        print("⚠️ Could not find log channel to send startup log.")
        for msg in messages:
            print(msg)

async def load_cogs() -> list[str]:
    logs = []
    for cog in os.listdir("cogs"):
        if cog.endswith(".py") and not cog.startswith("__"):
            cog_name = cog[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                logs.append(f"✅ Loaded cog `{cog_name}` successfully.")
            except Exception as e:
                error_msg = f"❌ Failed to load cog `{cog_name}`. Error: {e}"
                logs.append(error_msg)
                if DEBUG:
                    import traceback
                    traceback.print_exc()
    if DEBUG:
        for cog in os.listdir("test_cogs"):
            if cog.endswith(".py") and not cog.startswith("__"):
                cog_name = cog[:-3]
                try:
                    await bot.load_extension(f"test_cogs.{cog_name}")
                    logs.append(f"✅ Loaded test cog `{cog_name}` successfully.")
                except Exception as e:
                    error_msg = f"❌ Failed to load test cog `{cog_name}`. Error: {e}"
                    logs.append(error_msg)
                    import traceback
                    traceback.print_exc()
    return logs

@bot.event
async def on_ready():
    try:
        guild = discord.Object(id=GUILD_ID)
        
        # Sync commands
        synced = await tree.sync(guild=guild)
        
        sync_msg = f"✅ Synced {len(synced)} command(s) for guild `{GUILD_ID}`. Logged in as {bot.user}."
        startup_logs.append(sync_msg)
        await send_to_log_channel(startup_logs)
        
    except Exception as e:
        error_msg = f"❌ Error in on_ready: {e}"
        print(error_msg)
        if DEBUG:
            import traceback
            traceback.print_exc()

async def main():
    global startup_logs
    startup_logs = await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())