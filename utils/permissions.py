from aiogram.types import Message
from config import OWNER_ID

async def check_bot_admin(message: Message, bot):
    bot_member = await message.chat.get_member(bot.id)
    return bot_member.status in ["administrator", "creator"]

async def is_admin(message: Message):
    if message.from_user.id == OWNER_ID:
        return True
    member = await message.chat.get_member(message.from_user.id)
    return member.status in ["administrator", "creator"]

async def can_act_on_user(message: Message, target_user):
    # Cannot act on self
    if target_user.id == message.from_user.id:
        await message.reply("You cannot act on yourself.")
        return False
    # Cannot act on bot
    if target_user.is_bot:
        await message.reply("You cannot act on a bot.")
        return False
    # Check target admin status
    target_member = await message.chat.get_member(target_user.id)
    if target_member.status in ["administrator", "creator"]:
        # If target is admin, check if current user is owner or higher
        if message.from_user.id == OWNER_ID:
            return True
        if target_member.status == "creator":
            await message.reply("You cannot act on the group owner.")
            return False
        # Compare admin ranks (simplified: only allow owner to act on admins)
        if message.from_user.id != OWNER_ID:
            await message.reply("You cannot act on another admin.")
            return False
    return True
