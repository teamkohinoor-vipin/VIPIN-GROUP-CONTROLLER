import os
import aiosqlite
from config import DB_PATH

# ✅ Ensure directory exists (important for Railway)
dir_name = os.path.dirname(DB_PATH)
if dir_name:
    os.makedirs(dir_name, exist_ok=True)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            settings TEXT DEFAULT '{}',
            warn_limit INTEGER DEFAULT 3,
            flood_limit INTEGER DEFAULT 5,
            rules TEXT DEFAULT '',
            welcome_enabled INTEGER DEFAULT 1,
            goodbye_enabled INTEGER DEFAULT 1,
            anti_spam_enabled INTEGER DEFAULT 1,
            filter_enabled INTEGER DEFAULT 1,
            verification_enabled INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            group_id INTEGER,
            user_id INTEGER,
            admin_id INTEGER,
            reason TEXT,
            timestamp INTEGER,
            PRIMARY KEY (group_id, user_id, timestamp)
        )
        """)

        await db.commit()
