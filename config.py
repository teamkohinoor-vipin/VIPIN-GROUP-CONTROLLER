import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN found in environment variables")

# Database file
DB_PATH = "data/bot.db"  # will be created automatically

# Log channel ID (optional)
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
if LOG_CHANNEL_ID:
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)

# Default settings
DEFAULT_WARN_LIMIT = 3
DEFAULT_FLOOD_LIMIT = 5  # messages per 5 seconds
DEFAULT_ANTI_SPAM = True
DEFAULT_WELCOME = True
DEFAULT_GOODBYE = True
DEFAULT_FILTER = True
DEFAULT_VERIFICATION = False
DEFAULT_CAPTCHA_TIMEOUT = 60  # seconds

# Welcome message template
WELCOME_MESSAGE = "Welcome {name} to {group}! Please verify yourself by clicking the button below."
GOODBYE_MESSAGE = "Goodbye {name}!"

# Time formats for timed bans/mutes
TIME_UNITS = {
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}

# Bot owner ID (optional, for super admin commands)
OWNER_ID = os.getenv("OWNER_ID")
if OWNER_ID:
    OWNER_ID = int(OWNER_ID)