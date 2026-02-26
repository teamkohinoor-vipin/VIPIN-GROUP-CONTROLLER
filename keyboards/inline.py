from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_panel():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👮 Moderation", callback_data="panel_mod"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="panel_settings"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Stats", callback_data="panel_stats"),
        InlineKeyboardButton(text="❌ Close", callback_data="panel_close"),
    )
    return builder.as_markup()

def moderation_panel():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🚫 Ban", callback_data="mod_ban"),
        InlineKeyboardButton(text="🔇 Mute", callback_data="mod_mute"),
    )
    builder.row(
        InlineKeyboardButton(text="⚠️ Warn", callback_data="mod_warn"),
        InlineKeyboardButton(text="👢 Kick", callback_data="mod_kick"),
    )
    builder.row(
        InlineKeyboardButton(text="📌 Pin", callback_data="mod_pin"),
        InlineKeyboardButton(text="📍 Unpin", callback_data="mod_unpin"),
    )
    builder.row(
        InlineKeyboardButton(text="🧹 Purge", callback_data="mod_purge"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="panel_main"),
    )
    return builder.as_markup()

def settings_panel(settings: dict):
    builder = InlineKeyboardBuilder()
    # Toggle buttons with current status
    builder.row(
        InlineKeyboardButton(
            text=f"🛡 AntiSpam: {'ON' if settings['anti_spam_enabled'] else 'OFF'}",
            callback_data="toggle_antispam"
        ),
        InlineKeyboardButton(
            text=f"👋 Welcome: {'ON' if settings['welcome_enabled'] else 'OFF'}",
            callback_data="toggle_welcome"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f"🔐 Verify: {'ON' if settings['verification_enabled'] else 'OFF'}",
            callback_data="toggle_verify"
        ),
        InlineKeyboardButton(
            text=f"🧹 Filter: {'ON' if settings['filter_enabled'] else 'OFF'}",
            callback_data="toggle_filter"
        ),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Advanced", callback_data="settings_advanced"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="panel_main"),
    )
    return builder.as_markup()

def advanced_settings_panel():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Set Warn Limit", callback_data="set_warn_limit"),
        InlineKeyboardButton(text="Set Flood Limit", callback_data="set_flood_limit"),
    )
    builder.row(
        InlineKeyboardButton(text="Set Rules", callback_data="set_rules"),
        InlineKeyboardButton(text="⬅️ Back", callback_data="panel_settings"),
    )
    return builder.as_markup()

def verification_keyboard(chat_id, user_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Verify", callback_data=f"verify_{chat_id}_{user_id}")
    return builder.as_markup()

def close_button():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ Close", callback_data="panel_close")]])
