from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from filters import IsGroup
from database import get_group_settings, get_command, list_commands, add_command, remove_command
from utils.permissions import is_admin

router = Router()

# ID command
@router.message(Command("id"), IsGroup())
async def cmd_id(message: Message):
    text = f"Chat ID: `{message.chat.id}`\n"
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        text += f"User: {user.full_name} (`{user.id}`)"
    else:
        text += f"Your ID: `{message.from_user.id}`"
    await message.reply(text)

# Info command
@router.message(Command("info"), IsGroup())
async def cmd_info(message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user
    member = await message.chat.get_member(user.id)
    text = f"**User Info**\n"
    text += f"Name: {user.full_name}\n"
    text += f"ID: `{user.id}`\n"
    text += f"Status: {member.status}\n"
    text += f"Joined: {member.joined_date}"
    await message.reply(text)

# Admins list
@router.message(Command("admins"), IsGroup())
async def cmd_admins(message: Message):
    admins = await message.chat.get_administrators()
    text = "**Admins:**\n"
    for admin in admins:
        text += f"- {admin.user.full_name} (`{admin.user.id}`)\n"
    await message.reply(text)

# Report
@router.message(Command("report"), IsGroup())
async def cmd_report(message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to report it.")
    admins = await message.chat.get_administrators()
    report_text = f"🚨 Report from {message.from_user.full_name}\n"
    report_text += f"Message: {message.reply_to_message.text or 'Media'}\n"
    report_text += f"Link: https://t.me/c/{str(message.chat.id)[4:]}/{message.reply_to_message.message_id}"
    for admin in admins:
        if not admin.user.is_bot:
            try:
                await message.bot.send_message(admin.user.id, report_text)
            except:
                pass
    await message.reply("Report sent to admins.")

# Rules
@router.message(Command("rules"), IsGroup())
async def cmd_rules(message: Message):
    settings = await get_group_settings(message.chat.id)
    rules = settings.get("rules", "No rules set.")
    await message.reply(f"📜 Rules:\n{rules}")

# Set rules (admin)
@router.message(Command("setrules"), IsGroup())
async def cmd_setrules(message: Message):
    if not await is_admin(message):
        return
    if len(message.text.split()) < 2:
        return await message.reply("Please provide the rules text.")
    rules = message.text.split(maxsplit=1)[1]
    await update_group_setting(message.chat.id, "rules", rules)
    await message.reply("Rules updated.")

# Custom commands
@router.message(Command("addcommand"), IsGroup())
async def cmd_addcommand(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        return await message.reply("Usage: /addcommand <command> <response>")
    command = parts[1].lower()
    response = parts[2]
    await add_command(message.chat.id, command, response)
    await message.reply(f"✅ Command /{command} added.")

@router.message(Command("delcommand"), IsGroup())
async def cmd_delcommand(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply("Usage: /delcommand <command>")
    command = parts[1].lower()
    await remove_command(message.chat.id, command)
    await message.reply(f"✅ Command /{command} deleted.")

@router.message(Command("commands"), IsGroup())
async def cmd_commands(message: Message):
    cmds = await list_commands(message.chat.id)
    if cmds:
        text = "Custom commands:\n" + "\n".join([f"/{cmd}" for cmd in cmds])
    else:
        text = "No custom commands."
    await message.reply(text)

# Handle custom commands dynamically
@router.message(IsGroup())
async def handle_custom_commands(message: Message):
    if message.text and message.text.startswith("/"):
        cmd = message.text[1:].split()[0].lower()
        response = await get_command(message.chat.id, cmd)
        if response:
            await message.reply(response)
