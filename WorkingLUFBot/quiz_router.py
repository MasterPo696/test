import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.database import Database
from config import TOKEN, ETH_WALLET, sticker_pack, ProfileCreation
import app.keyboards.keyboards as kb
from aiogram import Bot, Dispatcher, types, F
# Configure logging
from texts.text_generation import greetings_reply

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from app.profile.exp import user_level
from app.chats.call_friends import inline_friends_keyboard
from app.profile.channel import check_user_in_channel
# from texts.text_generation import unknown_text_list
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()
quiz_router = Router()

@quiz_router.message(F.text)
async def handle_quiz_request():
    
    pass