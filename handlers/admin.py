from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from filters import IsGroup, IsAdmin
from keyboards.inline import main_panel, moderation_panel, settings_panel, advanced_settings_panel, close_button
from database import get_group_settings, update_group_setting, get_all_stats, increment_stat
from utils.logger import log_action
from config import LOG_CHANNEL_ID

import re

router = Router()

class SettingsFSM(StatesGroup):
    waiting_warn_limit = State()
    waiting_flood_limit = State()
    waiting_rules = State()

# /panel command
@router.message(Command("panel"), IsGroup(), IsAdmin())
async def cmd_panel(message: Message):
    await message.reply("🛠 Admin Panel", reply_markup=main_panel())

# Callback handlers
@router.callback_query(F.data == "panel_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("🛠 Admin Panel", reply_markup=main_panel())
    await callback.answer()

@router.callback_query(F.data == "panel_mod")
async def open_moderation(callback: CallbackQuery):
    await callback.message.edit_text("👮 Moderation Panel", reply_markup=moderation_panel())
    await callback.answer()

@router.callback_query(F.data == "panel_settings")
async def open_settings(callback: CallbackQuery):
    settings = await get_group_settings(callback.message.chat.id)
    await callback.message.edit_text("⚙️ Settings Panel", reply_markup=settings_panel(settings))
    await callback.answer()

@router.callback_query(F.data == "settings_advanced")
async def open_advanced(callback: CallbackQuery):
    await callback.message.edit_text("⚙️ Advanced Settings", reply_markup=advanced_settings_panel())
    await callback.answer()

@router.callback_query(F.data == "panel_stats")
async def show_stats(callback: CallbackQuery):
    stats = await get_all_stats(callback.message.chat.id)
    total_members = await callback.message.chat.get_member_count()
    text = f"📊 **Group Stats**\n\n"
    text += f"👥 Total members: {total_members}\n"
    text += f"🚫 Total bans: {stats.get('total_bans', 0)}\n"
    text += f"⚠️ Total warnings: {stats.get('total_warnings', 0)}\n"
    text += f"🗑 Deleted messages: {stats.get('deleted_messages', 0)}"
    await callback.message.edit_text(text, reply_markup=close_button())
    await callback.answer()

@router.callback_query(F.data == "panel_close")
async def close_panel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()

# Toggle settings
@router.callback_query(F.data.startswith("toggle_"))
async def toggle_setting(callback: CallbackQuery):
    setting = callback.data.replace("toggle_", "")
    chat_id = callback.message.chat.id
    settings = await get_group_settings(chat_id)
    key_map = {
        "antispam": "anti_spam_enabled",
        "welcome": "welcome_enabled",
        "verify": "verification_enabled",
        "filter": "filter_enabled",
    }
    db_key = key_map.get(setting)
    if not db_key:
        await callback.answer("Invalid setting")
        return
    current = settings[db_key]
    new_value = 0 if current else 1
    await update_group_setting(chat_id, db_key, new_value)
    # Update message
    settings[db_key] = bool(new_value)
    await callback.message.edit_reply_markup(reply_markup=settings_panel(settings))
    await callback.answer(f"✅ {setting.capitalize()} toggled {'ON' if new_value else 'OFF'}")

# Advanced settings callbacks
@router.callback_query(F.data == "set_warn_limit")
async def ask_warn_limit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Send the new warn limit (integer):")
    await state.set_state(SettingsFSM.waiting_warn_limit)
    await callback.answer()

@router.message(SettingsFSM.waiting_warn_limit, IsGroup(), IsAdmin())
async def set_warn_limit(message: Message, state: FSMContext):
    try:
        limit = int(message.text)
        await update_group_setting(message.chat.id, "warn_limit", limit)
        await message.reply(f"✅ Warn limit set to {limit}")
        await state.clear()
    except ValueError:
        await message.reply("❌ Invalid number. Please send an integer.")

@router.callback_query(F.data == "set_flood_limit")
async def ask_flood_limit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Send the new flood limit (messages per 5 seconds):")
    await state.set_state(SettingsFSM.waiting_flood_limit)
    await callback.answer()

@router.message(SettingsFSM.waiting_flood_limit, IsGroup(), IsAdmin())
async def set_flood_limit(message: Message, state: FSMContext):
    try:
        limit = int(message.text)
        await update_group_setting(message.chat.id, "flood_limit", limit)
        await message.reply(f"✅ Flood limit set to {limit}")
        await state.clear()
    except ValueError:
        await message.reply("❌ Invalid number.")

@router.callback_query(F.data == "set_rules")
async def ask_rules(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Send the new rules text:")
    await state.set_state(SettingsFSM.waiting_rules)
    await callback.answer()

@router.message(SettingsFSM.waiting_rules, IsGroup(), IsAdmin())
async def set_rules(message: Message, state: FSMContext):
    await update_group_setting(message.chat.id, "rules", message.text)
    await message.reply("✅ Rules updated.")
    await state.clear()
