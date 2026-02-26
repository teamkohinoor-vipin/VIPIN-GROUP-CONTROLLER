from aiogram import Router, F
from aiogram.types import CallbackQuery
from database import add_verified
import time

router = Router()

@router.callback_query(F.data.startswith("verify_"))
async def verify_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    chat_id = int(parts[1])
    user_id = int(parts[2])
    if callback.from_user.id != user_id:
        await callback.answer("This verification is not for you.", show_alert=True)
        return
    await add_verified(chat_id, user_id, int(time.time()))
    await callback.message.edit_text("✅ You have been verified! Welcome.")
    await callback.answer("Verified!")
