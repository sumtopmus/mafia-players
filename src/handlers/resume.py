from datetime import datetime
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, TypeHandler
from openai import OpenAI

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


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE, nickname: str) -> State:
    """Basic admin resume command."""
    log('resume')
    # System prompt
    with open(settings.PLAYER_ANALYSIS_PROMPT_PATH, 'r') as file:
        system_prompt = file.read()
    system_message = {
        "role": "system",
        "content": [{
            "type": "text",
            "text": system_prompt}]}
    # Games description
    games_description = f'Ник игрока: {nickname}\n\n'
    for game in context.user_data['players'][nickname]:
        timestamp = datetime.fromisoformat(game['timestamp']).strftime(settings.DATETIME_FORMAT)
        games_description += f'Игра: {timestamp}\n'
        games_description += f'Тип: {game['game_type']}\n'
        games_description += f'Карта: {game['card']}\n'
        games_description += f'Место: {game['number']}\n'
        games_description += f'Описание: {game['description']}\n\n'
    user_message = {
        "role": "user",
        "content": [{
            "type": "text",
            "text": games_description}]}
    # OpenAI API call
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[system_message, user_message],
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    # Send the response
    await update.effective_user.send_message(response.choices[0].message.content)
    return ConversationHandler.END