import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN, ProfileCreation, ETH_WALLET, sticker_pack, ProfileMaking
import app.keyboards.keyboards as kb
from aiogram import Bot, Dispatcher, types, F
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from app.profile.exp import user_level
from app.chats.call_friends import inline_friends_keyboard
from app.profile.channel import check_user_in_channel
ref_router = Router()
from db.database import Database as db


