import logging
from config import LOG_CHANNEL_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def log_action(chat_id, action, target_user, admin_user, reason="", duration=0):
    log_text = f"**#{action.upper()}**\n"
    log_text += f"User: {target_user.full_name} (`{target_user.id}`)\n"
    log_text += f"Admin: {admin_user.full_name} (`{admin_user.id}`)\n"
    log_text += f"Chat: `{chat_id}`\n"
    log_text += f"Reason: {reason}\n"
    if duration:
        log_text += f"Duration: {duration} seconds\n"
    logger.info(log_text)
    if LOG_CHANNEL_ID:
        try:
            await bot.send_message(LOG_CHANNEL_ID, log_text)
        except:
            pass
