import os
import aiosqlite
import json
import time
from config import DB_PATH

# ✅ Ensure directory exists
dir_name = os.path.dirname(DB_PATH)
if dir_name:
    os.makedirs(dir_name, exist_ok=True)


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            settings TEXT DEFAULT '{}',
            warn_limit INTEGER DEFAULT 3
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            group_id INTEGER,
            user_id INTEGER,
            admin_id INTEGER,
            reason TEXT,
            timestamp INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS mutes (
            group_id INTEGER,
            user_id INTEGER,
            until INTEGER,
            PRIMARY KEY (group_id, user_id)
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            group_id INTEGER,
            user_id INTEGER,
            admin_id INTEGER,
            reason TEXT,
            timestamp INTEGER,
            duration INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            group_id INTEGER,
            key TEXT,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (group_id, key)
        )
        """)

        await db.commit()


# ================= WARNINGS =================

async def add_warning(group_id, user_id, admin_id, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings VALUES (?, ?, ?, ?, ?)",
            (group_id, user_id, admin_id, reason, int(time.time()))
        )
        await db.commit()


async def get_warnings_count(group_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM warnings WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        row = await cursor.fetchone()
        return row[0] if row else 0


async def reset_warnings(group_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warnings WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        await db.commit()


# ================= MUTES =================

async def add_mute(group_id, user_id, until):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO mutes VALUES (?, ?, ?)",
            (group_id, user_id, until)
        )
        await db.commit()


async def remove_mute(group_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM mutes WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        await db.commit()


async def get_mute_until(group_id, user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT until FROM mutes WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


# ================= BANS =================

async def add_ban(group_id, user_id, admin_id, reason, duration=0):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bans VALUES (?, ?, ?, ?, ?, ?)",
            (group_id, user_id, admin_id, reason, int(time.time()), duration)
        )
        await db.commit()


# ================= STATS =================

async def increment_stat(group_id, key):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO stats (group_id, key, value)
            VALUES (?, ?, 1)
            ON CONFLICT(group_id, key)
            DO UPDATE SET value = value + 1
        """, (group_id, key))
        await db.commit()
