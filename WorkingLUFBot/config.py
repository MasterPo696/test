import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ChatMember
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import Bot, Dispatcher, Router
from db.database import Database
from aiogram.fsm.state import State, StatesGroup
import app.keyboards.keyboards as kb

sticker0 = "CAACAgQAAxkBAAIJUmbVXeF-yExM2Lvbr-n-rJFc83JBAAKfGQACKQ2oUtN9SrcNi7jdNQQ"
sticker1 = "CAACAgQAAxkBAAIJVGbVXeJZcgt9lG3-tLPhimGa3uBMAALLFAACI_CoUt9JFDV3tKp9NQQ"
sticker2 = "CAACAgQAAxkBAAIJWGbVXeO_LWCMlK7Ek3gk0Su8gE3gAALsGgAC8LepUhmqRg96ZVP1NQQ"
sticker3 = "CAACAgQAAxkBAAIJVmbVXeLAUXTQkFjZ3DPu9zOhovqfAAKbFAAC7_apUnu5-dj9jlATNQQ"
sticker_pack = [sticker0, sticker1, sticker2, sticker3]
emoji_list = ["😰", "🪙", "🔠","😋", "😛", "<3"]
ETH_WALLET = "0x885457f96f31Ec0Fa324f55b1B82E35107547F90"

MY_WALLET = "TRykwnn2CxnnUTQbXc5Git6iJxfxoX596i"
api_key = 'c947ac43-88ea-49ff-877a-e13c83369626'


LINK = "https://example.com"
TOKEN = "7171732387:AAHRC__AlW6_bTTDQDljIRVKqg5_CdefOws"
CHANNEL_ID = '@luf_zone'
WITHDRAW_GROUP_ID = '-4581053989'

level_points = [0, 1, 3, 5, 8, 12, 18]
text = " Now you can do bla bla bla!"


# Define states
class ProfileMaking(StatesGroup):
    name = State()
    gender = State()
    searching_for = State()
    hetero = State()
    photo = State()
    report = State()
    referral_id = State()

class ProfileChanging(StatesGroup):
    name = State()
    gender = State()
    looking_for = State()


class ProfileCreation(StatesGroup):
    name = State()
    report = State()
    gender = State()
    level = State()
    picture = State()
    picture_proving = State()

db = Database()
bot = Bot(token=TOKEN)
dp = Dispatcher()
database = Database()
router = Router()
exp_router = Router()

