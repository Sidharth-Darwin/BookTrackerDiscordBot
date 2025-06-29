import os
import discord
from dotenv import load_dotenv

# ---------------- Load Environment Variables ----------------
load_dotenv(".env")
DEBUG: bool = os.getenv("DEBUG", False) in ("True", "true", "1")
TOKEN: str = os.getenv("DISCORD_BOT_TOKEN") or ""
GUILD_ID: int = int(os.getenv("ALLOWED_GUILD_ID") or 0)
LOG_CHANNEL_ID: int = int(os.getenv("LOG_CHANNEL_ID") or 0)
CHANNEL_ID: int = int(os.getenv("ALLOWED_TEXT_CHANNEL_ID") or 0)
WELCOME_CHANNEL_ID: int = int(os.getenv("WELCOME_CHANNEL_ID") or 0)
GOOGLE_SHEETS_CRED_PATH = os.getenv("GOOGLE_SHEETS_CRED_PATH","service_account.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")
GOOGLE_SHEET_WORKSHEET = os.getenv("GOOGLE_SHEET_WORKSHEET", "Sheet1")

# ----------------- Constants ----------------
EXCEL_FILE: str = "data/reading_data.xlsx"
GENRE_FILE: str = "data/genres.csv"
MAX_FIELDS: int = 25  # Max fields per embed in progress command
DATE_CUTOFF_DAYS: int = 45  # 45 days in progress command
STATUS_MAP: dict[int, str] = {0: "Shelved", 1: "Reading", 2: "Finished"}
ENTRY_ROLE_NAME = "Reader"
TEMPLATE_PATH = "resources/template.jpeg"

# ---------------- Bot Setup ----------------
INTENTS = discord.Intents.default()
INTENTS.members = True
