from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from database import get_group_settings, add_verified
from keyboards.inline import verification_keyboard
from config import WELCOME_MESSAGE, GOODBYE_MESSAGE
import time

router = Router()

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_user_join(event: ChatMemberUpdated):
    chat = event.chat
    user = event.new_chat_member.user
    settings = await get_group_settings(chat.id)
    if not settings["welcome_enabled"]:
        return
    # Check verification
    if settings["verification_enabled"]:
        # Send captcha
        await send_verification(chat.id, user)
    else:
        # Send normal welcome
        text = WELCOME_MESSAGE.format(name=user.full_name, group=chat.title)
        await event.bot.send_message(chat.id, text)

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def on_user_leave(event: ChatMemberUpdated):
    chat = event.chat
    user = event.old_chat_member.user
    settings = await get_group_settings(chat.id)
    if settings.get("goodbye_enabled", True):
        text = GOODBYE_MESSAGE.format(name=user.full_name)
        await event.bot.send_message(chat.id, text)

async def send_verification(chat_id: int, user):
    # Simple button captcha
    keyboard = verification_keyboard(chat_id, user.id)
    text = f"Welcome {user.full_name}! Please click the button to verify you're human."
    msg = await event.bot.send_message(chat_id, text, reply_markup=keyboard)
    # Schedule kick after timeout
    asyncio.create_task(auto_kick_unverified(chat_id, user.id, msg.message_id))

async def auto_kick_unverified(chat_id, user_id, msg_id, timeout=60):
    await asyncio.sleep(timeout)
    # Check if user is verified (we can store in DB)
    if not await is_verified(chat_id, user_id):
        try:
            await bot.kick_chat_member(chat_id, user_id)
            await bot.unban_chat_member(chat_id, user_id)  # kick
            await bot.edit_message_text("User kicked for not verifying.", chat_id, msg_id)
        except:
            pass
