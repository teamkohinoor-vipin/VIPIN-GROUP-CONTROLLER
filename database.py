import os
import aiosqlite
import json
import time
from config import DB_PATH

# ✅ Ensure directory exists (Railway safe)
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

        await db.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            group_id INTEGER,
            key TEXT,
            value INTEGER DEFAULT 0,
            PRIMARY KEY (group_id, key)
        )
        """)

        await db.commit()


# ================= GROUP SETTINGS =================

async def get_group_settings(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM groups WHERE group_id = ?",
            (group_id,)
        )
        row = await cursor.fetchone()

        if not row:
            await db.execute(
                "INSERT INTO groups (group_id) VALUES (?)",
                (group_id,)
            )
            await db.commit()
            return await get_group_settings(group_id)

        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))


async def update_group_setting(group_id: int, key: str, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE groups SET {key} = ? WHERE group_id = ?",
            (value, group_id)
        )
        await db.commit()


# ================= WARNINGS =================

async def add_warning(group_id: int, user_id: int, admin_id: int, reason: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings VALUES (?, ?, ?, ?, ?)",
            (group_id, user_id, admin_id, reason, int(time.time()))
        )
        await db.commit()


async def get_warnings(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT * FROM warnings WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        return await cursor.fetchall()


async def clear_warnings(group_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warnings WHERE group_id = ? AND user_id = ?",
            (group_id, user_id)
        )
        await db.commit()


# ================= STATS =================

async def increment_stat(group_id: int, key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO stats (group_id, key, value)
            VALUES (?, ?, 1)
            ON CONFLICT(group_id, key)
            DO UPDATE SET value = value + 1
        """, (group_id, key))
        await db.commit()


async def get_all_stats(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT key, value FROM stats WHERE group_id = ?",
            (group_id,)
        )
        rows = await cursor.fetchall()
        return {key: value for key, value in rows}
