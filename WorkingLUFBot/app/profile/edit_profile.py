import logging
from aiogram import Bot, Dispatcher, types, Router

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN, ETH_WALLET, sticker_pack
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
from config import ProfileChanging
from db.database import Database

db = Database()
profile_router = Router()

def get_gender_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="male"),
         InlineKeyboardButton(text="Female", callback_data="female")]
    ])
    return keyboard


@profile_router.message(Command("edit"))
async def start(message: Message):
    start_text = "<b>Here you can /edit info about urself.</b>"
    await message.answer(start_text, parse_mode="HTML", reply_markup=kb.edit)


@profile_router.callback_query(F.data == "edit_name")
async def edit_name(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    profile = db.get_profile(user_id)
    await call_back.message.reply(f"Your name is {profile[1]}, write down your NEW name, to change it")
    await state.set_state(ProfileChanging.name)

@profile_router.message(ProfileChanging.name)
async def get_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text
    await state.update_data(name=name)
    db.update_name(name, user_id)
    await message.reply(f"Your name was changed to <b>{name}</b>", parse_mode="HTML")
    profile = db.get_profile(user_id)
    await state.clear()

@profile_router.callback_query(F.data == "edit_gender")
async def edit_gender(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    profile = db.get_profile(user_id)
    await call_back.message.reply(
    f"❗️ <b>{profile[1]}, due to fraud concerns, please contact support with a valid reason for your gender change request.</b>\n\n"
    "Send a brief explanation to our support team. We'll review it promptly.\n\n"
    "Thank you for your patience. Support responds in queue order.",
    parse_mode="HTML", reply_markup=kb.support
)
    
    # await call_back.message.reply("<b>Please, choose your new gender:</b>", parse_mode="HTML", reply_markup=get_gender_keyboard())
    # await state.set_state(ProfileChanging.gender)


@profile_router.callback_query(F.data == "looking_for")
async def edit_looking_for(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    profile = db.get_profile(user_id)
    await call_back.message.reply("<b>Please, choose the gender you are looking for:</b>", parse_mode="HTML", reply_markup=get_gender_keyboard())
    await state.set_state(ProfileChanging.looking_for)
    


@profile_router.callback_query(F.data.in_(['male', 'female']))
async def handle_gender_choice(call_back: CallbackQuery, state: FSMContext):
    user_id = call_back.from_user.id
    gender = call_back.data
    
    if await state.get_state() == ProfileChanging.gender:
        # Update the user's gender
        db.update_gender(user_id, gender)
        await call_back.message.answer(f"<b>Your gender was changed to {gender.capitalize()}.</b>", parse_mode="HTML")
    elif await state.get_state() == ProfileChanging.looking_for:
        # Update the gender the user is looking for
        db.update_interested_in(user_id, gender)
        await call_back.message.answer(f"<b>You are looking for {gender.capitalize()}s.</b>", parse_mode="HTML")

    # Clear state after processing
    await state.clear()
