import logging
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes, filters

from config import settings
from utils import log


def create_handlers() -> list:
    """Creates handlers that process admin's `show` command."""
    return [CommandHandler('show', show, filters.User(username=settings.ADMINS))]


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Basic admin show command."""
    log('show')
    log(context.user_data, level=logging.INFO)
