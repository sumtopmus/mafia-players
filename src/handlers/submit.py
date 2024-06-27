from datetime import datetime
from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, filters, MessageHandler, TypeHandler

from config import settings
import utils
from .common import Card, GameType, State, timeout, cancel


Card = Enum('Card', [
    'CITIZEN',
    'SHERIFF',
    'DON',
    'MAFIA',
])


GameType = Enum('GameType', [
    'CLUB',
    'TOURNAMENT',
    'ONLINE',
    'ONLINE_TOURNAMENT',
    'OTHER',
])


State = Enum('State', [
    'WAITING_FOR_NICKNAME',
    'WAITING_FOR_GAME_TYPE',
    'WAITING_FOR_CARD',
    'WAITING_FOR_NUMBER',
    'WAITING_FOR_DESCRIPTION',
])


def create_handlers() -> list:
    """Creates handlers that process `submit` command."""
    return [ConversationHandler(
        entry_points=[
            CommandHandler('submit', submit_request, filters.User(username=settings.USERS)),
        ],
        states={
            State.WAITING_FOR_NICKNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_nickname)],
            State.WAITING_FOR_GAME_TYPE: [CallbackQueryHandler(set_game_type)],
            State.WAITING_FOR_CARD: [CallbackQueryHandler(set_card)],
            State.WAITING_FOR_NUMBER: [CallbackQueryHandler(set_number)],
            State.WAITING_FOR_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_description)],
            ConversationHandler.TIMEOUT: [TypeHandler(Update, timeout)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel, filters.User(username=settings.USERS)),
        ],
        allow_reentry=True,
        conversation_timeout=settings.CONVERSATION_TIMEOUT,
        name="submit",
        per_chat=False,
        persistent=True)]


async def submit_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When a user starts the player's data submission."""
    utils.log('submit_request')
    context.user_data.setdefault('players', {})
    message = 'Пожалуйста, введите ник игрока.'
    await update.effective_user.send_message(message)
    return State.WAITING_FOR_NICKNAME


async def set_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> State:
    """When the nickname is submitted."""
    utils.log('set_nickname')
    nickname = update.message.text
    context.user_data['new_game'] = {
        'timestamp': datetime.now().isoformat(),
        'nickname': nickname,
    }
    message = (f'Выберите тип игры.')
    keyboard = [
        [
            InlineKeyboardButton("Клуб", callback_data=GameType.CLUB.name),
            InlineKeyboardButton("Турнир", callback_data=GameType.TOURNAMENT.name),
        ],
        [
            InlineKeyboardButton("Онлайн", callback_data=GameType.ONLINE.name),
            InlineKeyboardButton("Онлайн-турнир", callback_data=GameType.ONLINE_TOURNAMENT.name),
        ],
        [
            InlineKeyboardButton("Другой", callback_data=GameType.OTHER.name),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_user.send_message(message, reply_markup=reply_markup)
    return State.WAITING_FOR_GAME_TYPE    


async def set_game_type(update: Update, context: CallbackContext) -> State:
    """When the game type is submitted."""
    utils.log('set_game_type')
    await update.callback_query.answer()
    context.user_data['new_game']['game_type'] = update.callback_query.data
    message = f'На какой карте играл игрок?'
    keyboard = [
        [
            InlineKeyboardButton("Шериф", callback_data=Card.SHERIFF.name),
            InlineKeyboardButton("Мирный", callback_data=Card.CITIZEN.name),
        ],
        [
            InlineKeyboardButton("Дон", callback_data=Card.DON.name),
            InlineKeyboardButton("Мафия", callback_data=Card.MAFIA.name),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    return State.WAITING_FOR_CARD


async def set_card(update: Update, context: CallbackContext) -> State:
    """When the card is submitted."""
    utils.log('set_card')
    await update.callback_query.answer()
    context.user_data['new_game']['card'] = update.callback_query.data
    message = (f'На каком номере сыграл игрок?')
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=1),
            InlineKeyboardButton("2", callback_data=2),
            InlineKeyboardButton("3", callback_data=3),
            InlineKeyboardButton("4", callback_data=4),
            InlineKeyboardButton("5", callback_data=5),
        ],
        [
            InlineKeyboardButton("6", callback_data=6),
            InlineKeyboardButton("7", callback_data=7),
            InlineKeyboardButton("8", callback_data=8),
            InlineKeyboardButton("9", callback_data=9),
            InlineKeyboardButton("10", callback_data=10),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)    
    await update.callback_query.edit_message_text(message, reply_markup=reply_markup)
    return State.WAITING_FOR_NUMBER


async def set_number(update: Update, context: CallbackContext) -> State:
    """When the number is submitted."""
    utils.log('set_number')
    await update.callback_query.answer()
    context.user_data['new_game']['number'] = update.callback_query.data
    message = (f'Опишите действия игрока.')
    await update.callback_query.edit_message_text(message)
    return State.WAITING_FOR_DESCRIPTION


async def set_description(update: Update, context: CallbackContext) -> State:
    """When the description is submitted."""
    utils.log('set_description')
    context.user_data['new_game']['description'] = update.message.text
    new_game = context.user_data['new_game']
    nickname = new_game['nickname']
    context.user_data['players'].setdefault(nickname, [])
    context.user_data['players'][nickname].append(
        {k: v for k, v in new_game.items() if k != 'nickname'}
    )
    message = (f'База данных обновлена!')
    await update.effective_user.send_message(message)
    return ConversationHandler.END
