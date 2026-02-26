import os
import aiosqlite
import json
from config import DB_PATH

# Ensure the data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        # Groups table
        await db.execute('''
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
        ''')
        # Warnings table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                group_id INTEGER,
                user_id INTEGER,
                admin_id INTEGER,
                reason TEXT,
                timestamp INTEGER,
                PRIMARY KEY (group_id, user_id, timestamp)
            )
        ''')
        # Bans table (for stats)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bans (
                group_id INTEGER,
                user_id INTEGER,
                admin_id INTEGER,
                reason TEXT,
                timestamp INTEGER,
                duration INTEGER DEFAULT 0
            )
        ''')
        # Mutes table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS mutes (
                group_id INTEGER,
                user_id INTEGER,
                until INTEGER,
                PRIMARY KEY (group_id, user_id)
            )
        ''')
        # Custom commands table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS custom_commands (
                group_id INTEGER,
                command TEXT,
                response TEXT,
                PRIMARY KEY (group_id, command)
            )
        ''')
        # Verified users table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS verified (
                group_id INTEGER,
                user_id INTEGER,
                verified_at INTEGER,
                PRIMARY KEY (group_id, user_id)
            )
        ''')
        # Stats table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                group_id INTEGER,
                key TEXT,
                value INTEGER DEFAULT 0,
                PRIMARY KEY (group_id, key)
            )
        ''')
        await db.commit()

# --- Group settings ---
async def get_group_settings(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT settings, warn_limit, flood_limit, rules, welcome_enabled,
                   goodbye_enabled, anti_spam_enabled, filter_enabled, verification_enabled
            FROM groups WHERE group_id = ?
        ''', (group_id,))
        row = await cursor.fetchone()
        if row:
            return {
                "settings": json.loads(row[0]),
                "warn_limit": row[1],
                "flood_limit": row[2],
                "rules": row[3],
                "welcome_enabled": bool(row[4]),
                "goodbye_enabled": bool(row[5]),
                "anti_spam_enabled": bool(row[6]),
                "filter_enabled": bool(row[7]),
                "verification_enabled": bool(row[8]),
            }
        else:
            # Insert default settings
            default_settings = json.dumps({})
            await db.execute('''
                INSERT INTO groups (group_id, settings) VALUES (?, ?)
            ''', (group_id, default_settings))
            await db.commit()
            return {
                "settings": {},
                "warn_limit": 3,
                "flood_limit": 5,
                "rules": "",
                "welcome_enabled": True,
                "goodbye_enabled": True,
                "anti_spam_enabled": True,
                "filter_enabled": True,
                "verification_enabled": False,
            }

async def update_group_setting(group_id: int, key: str, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f'UPDATE groups SET {key} = ? WHERE group_id = ?', (value, group_id))
        await db.commit()

# --- Warnings ---
async def add_warning(group_id: int, user_id: int, admin_id: int, reason: str, timestamp: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO warnings (group_id, user_id, admin_id, reason, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (group_id, user_id, admin_id, reason, timestamp))
        await db.commit()

async def get_warnings_count(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?
        ''', (group_id, user_id))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def reset_warnings(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM warnings WHERE group_id = ? AND user_id = ?', (group_id, user_id))
        await db.commit()

# --- Mutes ---
async def add_mute(group_id: int, user_id: int, until: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO mutes (group_id, user_id, until)
            VALUES (?, ?, ?)
        ''', (group_id, user_id, until))
        await db.commit()

async def remove_mute(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM mutes WHERE group_id = ? AND user_id = ?', (group_id, user_id))
        await db.commit()

async def get_mute_until(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT until FROM mutes WHERE group_id = ? AND user_id = ?', (group_id, user_id))
        row = await cursor.fetchone()
        return row[0] if row else None

# --- Bans (stats) ---
async def add_ban(group_id: int, user_id: int, admin_id: int, reason: str, timestamp: int, duration: int = 0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO bans (group_id, user_id, admin_id, reason, timestamp, duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (group_id, user_id, admin_id, reason, timestamp, duration))
        # Increment stats
        await db.execute('''
            INSERT INTO stats (group_id, key, value)
            VALUES (?, 'total_bans', 1)
            ON CONFLICT(group_id, key) DO UPDATE SET value = value + 1
        ''', (group_id,))
        await db.commit()

# --- Custom commands ---
async def add_command(group_id: int, command: str, response: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO custom_commands (group_id, command, response)
            VALUES (?, ?, ?)
        ''', (group_id, command, response))
        await db.commit()

async def remove_command(group_id: int, command: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM custom_commands WHERE group_id = ? AND command = ?', (group_id, command))
        await db.commit()

async def get_command(group_id: int, command: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT response FROM custom_commands WHERE group_id = ? AND command = ?', (group_id, command))
        row = await cursor.fetchone()
        return row[0] if row else None

async def list_commands(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT command FROM custom_commands WHERE group_id = ?', (group_id,))
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# --- Verified users ---
async def add_verified(group_id: int, user_id: int, timestamp: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO verified (group_id, user_id, verified_at)
            VALUES (?, ?, ?)
        ''', (group_id, user_id, timestamp))
        await db.commit()

async def is_verified(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT 1 FROM verified WHERE group_id = ? AND user_id = ?', (group_id, user_id))
        return await cursor.fetchone() is not None

# --- Stats ---
async def increment_stat(group_id: int, key: str, inc: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO stats (group_id, key, value)
            VALUES (?, ?, ?)
            ON CONFLICT(group_id, key) DO UPDATE SET value = value + ?
        ''', (group_id, key, inc, inc))
        await db.commit()

async def get_stat(group_id: int, key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT value FROM stats WHERE group_id = ? AND key = ?', (group_id, key))
        row = await cursor.fetchone()
        return row[0] if row else 0

async def get_all_stats(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT key, value FROM stats WHERE group_id = ?', (group_id,))
        rows = await cursor.fetchall()
        return dict(rows)
