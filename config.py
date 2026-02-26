import os
from dotenv import load_dotenv

load_dotenv()

# Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

# ✅ Database path (Railway safe)
DB_PATH = "data/bot.db"

# Log channel ID (optional)
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
if LOG_CHANNEL_ID:
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)

# Default settings
DEFAULT_WARN_LIMIT = 3
DEFAULT_FLOOD_LIMIT = 5
DEFAULT_ANTI_SPAM = True
DEFAULT_WELCOME = True
DEFAULT_GOODBYE = True
DEFAULT_FILTER = True
DEFAULT_VERIFICATION = False
DEFAULT_CAPTCHA_TIMEOUT = 60

WELCOME_MESSAGE = "Welcome {name} to {group}! Please verify yourself by clicking the button below."
GOODBYE_MESSAGE = "Goodbye {name}!"

TIME_UNITS = {
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}

OWNER_ID = os.getenv("OWNER_ID")
if OWNER_ID:
    OWNER_ID = int(OWNER_ID)
