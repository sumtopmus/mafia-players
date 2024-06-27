from datetime import datetime
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, TypeHandler

from config import settings
from utils import log
from .common import State, cancel, timeout


def create_handlers() -> list:
    """Creates handlers that process admin's `resume` command."""
    return [ConversationHandler(
        entry_points=[
            CommandHandler('resume', resume_request, filters.User(username=settings.USERS)),
        ],
        states={
            State.WAITING_FOR_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_nickname)],
            ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel, filters.User(username=settings.USERS)),
        ],
        allow_reentry=True,
        conversation_timeout=settings.CONVERSATION_TIMEOUT,
        name="resume",
        per_chat=False,
        persistent=True)]


async def resume_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user request a resume."""
    log('resume_request')
    if len(context.args) > 0:
        nickname = ' '.join(context.args)
        log(f'nickname: {nickname}')
        await resume(update, context, nickname)
        return ConversationHandler.END
    else: 
        message = 'Введите никнейм игрока, информацию о котором вы хотите получить.'
        await update.effective_user.send_message(message)
        return State.WAITING_FOR_NICKNAME


async def set_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user sets a nickname."""
    log('set_nickname')
    nickname = update.message.text
    log(f'nickname: {nickname}')
    await resume(update, context, nickname)
    return ConversationHandler.END


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE, nickname: str) -> None:
    """Basic admin resume command."""
    log('resume')
    info = ''
    for game in context.user_data['players'][nickname]:
        timestamp = datetime.fromisoformat(game['timestamp']).strftime(settings.DATETIME_FORMAT)
        info += f'Игра: {timestamp}\n'
        info += f'Карта: {game['card']}\n'
        info += f'Место: {game['number']}\n'
        info += f'Описание: {game['description']}\n\n'
    message = (f'Информация об игроке {nickname}:\n\n' + info).strip()
    log(message, level=logging.INFO)
    await update.effective_user.send_message(message)
