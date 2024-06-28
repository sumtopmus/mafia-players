from enum import Enum
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
import utils


class Card(Enum):
    CITIZEN = 'Мирный житель'
    SHERIFF = 'Шериф'
    DON = 'Дон'
    MAFIA = 'Мафия'

    def __init__(self, card):
        self.card = card


class GameType(Enum):
    CLUB = 'Клубная'
    TOURNAMENT = 'Турнир'
    ONLINE = 'Онлайн'
    ONLINE_TOURNAMENT = 'Онлайн-турнир'
    OTHER = 'Другой'

    def __init__(self, type):
        self.type = type


State = Enum('State', [
    'WAITING_FOR_NICKNAME',
    'WAITING_FOR_GAME_TYPE',
    'WAITING_FOR_CARD',
    'WAITING_FOR_NUMBER',
    'WAITING_FOR_DESCRIPTION',
])


async def timeout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When the conversation timepout is exceeded."""
    utils.log('timeout')
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When a user cancels the process."""
    utils.log('cancel')
    message = (
        'Операция отменена. Вы можете отправить информацию об игроке с помощью команды /submit '
        'или же получить информацию об игроке с помощью команды /resume <nickname>.')
    await update.effective_user.send_message(message)
    return ConversationHandler.END
