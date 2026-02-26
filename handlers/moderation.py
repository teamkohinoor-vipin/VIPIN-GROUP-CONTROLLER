import asyncio
import re
from datetime import datetime, timedelta
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from filters import IsGroup, IsAdmin, IsBotAdmin
from database import add_warning, get_warnings_count, reset_warnings, add_mute, remove_mute, get_mute_until, add_ban, increment_stat
from utils.permissions import check_bot_admin, can_act_on_user
from utils.time_parser import parse_time
from utils.logger import log_action
from keyboards.inline import moderation_panel
from config import LOG_CHANNEL_ID

import time

router = Router()

# Helper to get replied user
async def get_target_user(message: Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    elif len(message.text.split()) >= 2:
        # Try to parse username or user id
        arg = message.text.split()[1]
        if arg.startswith("@"):
            # Not easy to get user by username without search, skip for now
            return None
        else:
            try:
                user_id = int(arg)
                return await message.bot.get_chat_member(message.chat.id, user_id)
            except:
                return None
    return None

# Ban command
@router.message(Command("ban"), IsGroup(), IsAdmin())
async def cmd_ban(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    target = await get_target_user(message)
    if not target:
        return await message.reply("Reply to a user or provide user ID.")
    if not await can_act_on_user(message, target.user):
        return
    # Parse duration and reason
    parts = message.text.split()
    reason = "No reason"
    duration = 0
    if len(parts) > 2:
        # Check if second part is time
        time_match = re.match(r'^(\d+)([mhdw])$', parts[2])
        if time_match:
            duration = parse_time(parts[2])
            reason = " ".join(parts[3:]) if len(parts) > 3 else "No reason"
        else:
            reason = " ".join(parts[2:])
    try:
        await message.chat.ban(target.user.id)
        await add_ban(message.chat.id, target.user.id, message.from_user.id, reason, int(time.time()), duration)
        await increment_stat(message.chat.id, "total_bans")
        # If duration, schedule unban
        if duration:
            asyncio.create_task(scheduled_unban(message.chat.id, target.user.id, duration, bot))
        await message.reply(f"✅ Banned {target.user.full_name}.\nReason: {reason}")
        await log_action(message.chat.id, "ban", target.user, message.from_user, reason, duration)
        # Auto-delete command
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Scheduled unban
async def scheduled_unban(chat_id, user_id, duration, bot):
    await asyncio.sleep(duration)
    try:
        await bot.unban_chat_member(chat_id, user_id)
        await remove_mute(chat_id, user_id)  # in case it was a mute
    except:
        pass

# Unban
@router.message(Command("unban"), IsGroup(), IsAdmin())
async def cmd_unban(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    try:
        user_id = int(message.text.split()[1])
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ Unbanned user {user_id}")
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Mute (restrict sending messages)
@router.message(Command("mute"), IsGroup(), IsAdmin())
async def cmd_mute(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    target = await get_target_user(message)
    if not target:
        return await message.reply("Reply to a user or provide user ID.")
    if not await can_act_on_user(message, target.user):
        return
    parts = message.text.split()
    duration = 0
    reason = "No reason"
    if len(parts) > 2:
        time_match = re.match(r'^(\d+)([mhdw])$', parts[2])
        if time_match:
            duration = parse_time(parts[2])
            reason = " ".join(parts[3:]) if len(parts) > 3 else "No reason"
        else:
            reason = " ".join(parts[2:])
    until_date = int(time.time()) + duration if duration else 0
    try:
        await bot.restrict_chat_member(
            message.chat.id,
            target.user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date if duration else None
        )
        if duration:
            await add_mute(message.chat.id, target.user.id, until_date)
        await message.reply(f"✅ Muted {target.user.full_name}.\nReason: {reason}")
        await log_action(message.chat.id, "mute", target.user, message.from_user, reason, duration)
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Unmute
@router.message(Command("unmute"), IsGroup(), IsAdmin())
async def cmd_unmute(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    target = await get_target_user(message)
    if not target:
        return await message.reply("Reply to a user or provide user ID.")
    try:
        await bot.restrict_chat_member(
            message.chat.id,
            target.user.id,
            permissions=ChatPermissions(can_send_messages=True)
        )
        await remove_mute(message.chat.id, target.user.id)
        await message.reply(f"✅ Unmuted {target.user.full_name}")
        await log_action(message.chat.id, "unmute", target.user, message.from_user)
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Warn
@router.message(Command("warn"), IsGroup(), IsAdmin())
async def cmd_warn(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    target = await get_target_user(message)
    if not target:
        return await message.reply("Reply to a user or provide user ID.")
    if not await can_act_on_user(message, target.user):
        return
    parts = message.text.split()
    reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason"
    timestamp = int(time.time())
    await add_warning(message.chat.id, target.user.id, message.from_user.id, reason, timestamp)
    warn_count = await get_warnings_count(message.chat.id, target.user.id)
    settings = await get_group_settings(message.chat.id)
    warn_limit = settings["warn_limit"]
    await message.reply(f"⚠️ {target.user.full_name} warned ({warn_count}/{warn_limit}).\nReason: {reason}")
    await increment_stat(message.chat.id, "total_warnings")
    await log_action(message.chat.id, "warn", target.user, message.from_user, reason)
    if warn_count >= warn_limit:
        # Auto mute
        await bot.restrict_chat_member(
            message.chat.id,
            target.user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await add_mute(message.chat.id, target.user.id, 0)  # permanent until unmute
        await message.reply(f"🔇 {target.user.full_name} auto-muted for reaching warn limit.")
        await reset_warnings(message.chat.id, target.user.id)

# Warnings command
@router.message(Command("warnings"), IsGroup())
async def cmd_warnings(message: Message):
    target = await get_target_user(message)
    if not target:
        target = message.from_user
    count = await get_warnings_count(message.chat.id, target.id)
    await message.reply(f"⚠️ {target.full_name} has {count} warning(s).")

# Kick
@router.message(Command("kick"), IsGroup(), IsAdmin())
async def cmd_kick(message: Message, bot: Bot):
    if not await check_bot_admin(message, bot):
        return await message.reply("❌ I'm not an admin here.")
    target = await get_target_user(message)
    if not target:
        return await message.reply("Reply to a user or provide user ID.")
    if not await can_act_on_user(message, target.user):
        return
    try:
        await bot.ban_chat_member(message.chat.id, target.user.id)
        await bot.unban_chat_member(message.chat.id, target.user.id)  # kick = ban then unban
        await message.reply(f"✅ Kicked {target.user.full_name}")
        await log_action(message.chat.id, "kick", target.user, message.from_user)
        await asyncio.sleep(5)
        await message.delete()
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Pin
@router.message(Command("pin"), IsGroup(), IsAdmin())
async def cmd_pin(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to pin.")
    try:
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        await message.reply("📌 Pinned.")
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Unpin
@router.message(Command("unpin"), IsGroup(), IsAdmin())
async def cmd_unpin(message: Message, bot: Bot):
    try:
        if message.reply_to_message:
            await bot.unpin_chat_message(message.chat.id, message.reply_to_message.message_id)
        else:
            await bot.unpin_chat_message(message.chat.id)
        await message.reply("📍 Unpinned.")
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Purge
@router.message(Command("purge"), IsGroup(), IsAdmin())
async def cmd_purge(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to purge from there.")
    try:
        start_id = message.reply_to_message.message_id
        end_id = message.message_id
        count = 0
        for msg_id in range(start_id, end_id + 1):
            try:
                await bot.delete_message(message.chat.id, msg_id)
                count += 1
                await asyncio.sleep(0.1)  # avoid flood
            except:
                pass
        await message.answer(f"✅ Purged {count} messages.")
        await increment_stat(message.chat.id, "deleted_messages", count)
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Del (delete replied)
@router.message(Command("del"), IsGroup(), IsAdmin())
async def cmd_del(message: Message, bot: Bot):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to delete.")
    try:
        await message.reply_to_message.delete()
        await message.delete()
        await increment_stat(message.chat.id, "deleted_messages", 1)
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# Callback handlers for moderation panel
@router.callback_query(F.data == "mod_ban")
async def panel_ban(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a user message to ban them.\nOr send /ban <user_id> <reason>")
    await callback.answer()

@router.callback_query(F.data == "mod_mute")
async def panel_mute(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a user message to mute them.\nYou can include time (e.g., /mute 1h spam)")
    await callback.answer()

@router.callback_query(F.data == "mod_warn")
async def panel_warn(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a user message to warn them.")
    await callback.answer()

@router.callback_query(F.data == "mod_kick")
async def panel_kick(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a user message to kick them.")
    await callback.answer()

@router.callback_query(F.data == "mod_pin")
async def panel_pin(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a message to pin it.")
    await callback.answer()

@router.callback_query(F.data == "mod_unpin")
async def panel_unpin(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a pinned message to unpin it, or use /unpin")
    await callback.answer()

@router.callback_query(F.data == "mod_purge")
async def panel_purge(callback: CallbackQuery):
    await callback.message.edit_text("Reply to a message to purge from there.")
    await callback.answer()
