import re
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from db.database import Database
from config import ProfileMaking
import app.keyboards.keyboards as kb

# Configuration
BANNED_TOPICS = [
    # Криптокошельки и криптовалюты
    'wallet', 'address', 'crypto', 'btc', 'bitcoin', 'eth', 'usdt', 'coinbase', 'metamask', 'private key', 'public key',
    
    # Номера телефонов и контакты
    'phone', 'number', 'contact', 'whatsapp', 'viber', 'telegram', 'sms', 'direct', 
    
    # Запретные и аморальные темы
    'prohibited', 'restricted', 'scam', 'fraud', 'hacking', 'illegal', 'sex', 'drugs', 'violence', 'explicit', 'adult', 'pornography', 'sister', 'uncle', 'daughter', 'teen'
]

# Регулярные выражения
BITCOIN_REGEX = re.compile(r'\b([13]|bc1)[a-zA-Z0-9]{26,35}\b', re.IGNORECASE)
ETHEREUM_REGEX = re.compile(r'\b0x[a-fA-F0-9]{40}\b', re.IGNORECASE)
USDT_REGEX = re.compile(r'\b([13]|bc1|0x)[a-zA-Z0-9]{26,40}\b', re.IGNORECASE)
XRP_REGEX = re.compile(r'\br[a-zA-Z0-9]{24,34}\b', re.IGNORECASE)
LTC_REGEX = re.compile(r'\b[Lm3][a-zA-Z0-9]{26,35}\b', re.IGNORECASE)
# PHONE_INTERNATIONAL_REGEX = re.compile(r'\+?\d{1,4}[\s.-]?\d{1,15}', re.IGNORECASE)
# PHONE_USA_REGEX = re.compile(r'\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}', re.IGNORECASE)
URL_REGEX = re.compile(r'https?://\S+')

BANNED_REGEX = [BITCOIN_REGEX, BITCOIN_REGEX, USDT_REGEX, XRP_REGEX, LTC_REGEX, URL_REGEX]



# Initialize database and router
database = Database()
rep_router = Router()

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def check_for_prohibited_content(text: str, user_id: int):
    for topic in BANNED_REGEX:
        if topic.search(text):
            chat = database.get_chat(user_id)
            partner_id = chat[1] if chat else None
            if not partner_id:
                profile = database.get_profile(user_id)
                partner_id = profile[5] if profile else None
            database.save_report(user_id, partner_id, topic, 1)   
            return f"The topic '{topic}' is not allowed."

    for topic in BANNED_TOPICS:
        if topic in text.lower():
            chat = database.get_chat(user_id)
            partner_id = chat[1] if chat else None
            if not partner_id:
                profile = database.get_profile(user_id)
                partner_id = profile[5] if profile else None
            database.save_report(user_id, partner_id, topic, 1)
            return f"The topic '{topic}' is not allowed."

    return None


from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  

# yes_no = InlineKeyboardBuilder(inline_keyboard=[
#     [InlineKeyboardButton(text="Yes", callback_data='yes')],[InlineKeyboardButton(text="No", callback_data='no')]])


@rep_router.callback_query()
async def callback_handler(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    profile = database.get_profile(user_id)
    partner_id = profile[5] if profile else None

    logger.debug(f"Callback handler - user: {user_id}, partner: {partner_id}")

    if query.data == 'like':
        logger.debug(f"User {user_id} liked user {partner_id}")
        database.add_like(user_id)
        await query.answer("You liked the user!")

    elif query.data == 'dislike':
        logger.debug(f"User {user_id} disliked user {partner_id}")
        database.add_dislike(user_id)
        await query.answer("You disliked the user!")

    elif query.data == 'follow':
        await query.message.answer("Are you sure, you want to add this person as a friend?", reply_markup=kb.rate)
        await state.set_state(ProfileMaking.report)
        logger.debug(f"State set to ProfileMaking.report for user {user_id}")

    try:
        await query.message.delete()
    except TelegramAPIError as e:
        logger.error(f"Failed to delete message: {e}")
    


# не работает!
@rep_router.message(ProfileMaking.report)
async def enter_report(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    report_message = message.text

    logger.debug(f"Received report from user {user_id}: {report_message}")

    profile = database.get_profile(user_id)
    if not profile:
        logger.warning(f"No profile found for user {user_id}")
        await message.answer("Could not find your profile. Please try again later.", reply_markup=kb.menu)
        await state.clear()
        return

    last_partner_id = profile[5] if profile else None
    logger.debug(f"Last partner ID for user {user_id}: {last_partner_id}")

    if last_partner_id:
        try:
            database.save_report(user_id, last_partner_id, report_message, 0)
            await message.answer("Your report has been submitted successfully.", reply_markup=kb.menu)
        except Exception as e:
            logger.error(f"Error saving report: {e}")
            await message.answer("There was an error while submitting your report. Please try again later.", reply_markup=kb.menu)
    else:
        logger.warning(f"No last_partner_id found for user {user_id}.")
        await message.answer("Could not submit the report. Please try again later.", reply_markup=kb.menu)

    await state.clear()
