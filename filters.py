from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID

class IsGroup(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ["group", "supergroup"]

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user.id == OWNER_ID:
            return True
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ["administrator", "creator"]

class IsBotAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        bot = await message.bot.me()
        member = await message.chat.get_member(bot.id)
        return member.status in ["administrator", "creator"]

class IsOwner(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.status == "creator"