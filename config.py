import os
import discord
from dotenv import load_dotenv

# ---------------- Environment Variables ----------------
load_dotenv(".env")

# ----------------- Constants ----------------
DEBUG: bool = os.getenv("DEBUG", False) in ("True", "true", "1")
TOKEN: str = os.getenv("DISCORD_BOT_TOKEN") or ""
GUILD_ID: int = int(os.getenv("ALLOWED_GUILD_ID") or 0)
LOG_CHANNEL_ID: int = int(os.getenv("LOG_CHANNEL_ID") or 0)
CHANNEL_ID: int = int(os.getenv("ALLOWED_TEXT_CHANNEL_ID") or 0)
EXCEL_FILE: str = "data/reading_data.xlsx"
GENRE_FILE: str = "data/genres.csv"
MAX_FIELDS: int = 25  # Max fields per embed in progress command
DATE_CUTOFF_DAYS: int = 45  # 45 days in progress command

# ---------------- Bot Setup ----------------
INTENTS = discord.Intents.default()
INTENTS.members = True
