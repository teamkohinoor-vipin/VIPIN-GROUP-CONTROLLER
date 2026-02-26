from aiogram import Router
from aiogram.types import ErrorEvent
import logging

router = Router()

@router.errors()
async def errors_handler(event: ErrorEvent):
    logging.error(f"Update {event.update} caused error {event.exception}")
    # Optionally notify admin
