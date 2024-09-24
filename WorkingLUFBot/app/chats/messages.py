import re
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot, Dispatcher, types, F
from db.database import Database
MAX_FREINDS = 5
# from app.chats.add_friends import add_friend_request
from brain.forbidden import check_for_prohibited_content
from texts.text_generation import sticker_responses, photo_responses, video_responses, document_responses
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  

BANNED_TOPICS = ['prohibited', 'banned', 'restricted', 'crypto', 'btc', 'bitcoin', 'eth', 'usdt', 'direct']  # Пример ключевых слов
URL_REGEX = re.compile(r'https?://\S+')
database = Database()
from config import bot
msg_router = Router()
from config import ProfileCreation
from aiogram.exceptions import TelegramAPIError
import app.keyboards.keyboards as kb

from app.profile.exp import award_exp
from config import sticker_pack
import logging
from datetime import datetime
from texts.text_generation import unknown_text_reply
from app.profile.referrals import ProfileMaking
from texts.text_generation import greetings_reply
from texts.text_generation import say_hi
from app.balance.local_balance.update_balance import update_balances
import random



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_message_count = {}
# created_time = ""    
      

# Все, что ниже в файл exp.py
class Tip(StatesGroup):
    user_id = State()
    amount = State()
    partner = State()


def is_greeting_word(word):
    if word.lower() in say_hi:
        return True

def get_current_time():
    return datetime.now()



# Handle callback for entering referral code
@msg_router.callback_query(lambda c: c.data == "enter_referral_code")
async def enter_referral_code_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Please send your referral code.")
    await state.set_state(ProfileMaking.referral_id)
    print(1)
    await callback_query.answer()

# Handle referral code submission
@msg_router.message(ProfileMaking.referral_id)
async def handle_referral_code(message: Message, state: FSMContext):
    user_id = message.from_user.id
    referral_code = message.text.strip()
    print(2)
    if database.user_exists(referral_code):
        if not database.user_exists(user_id):
            user_name = message.from_user.full_name
            await state.set_state(ProfileMaking.name)
            await state.update_data(name=user_name)
            await state.set_state(ProfileMaking.gender)
            await state.update_data(gender="Male")
            await state.update_data(referral_id=referral_code)
            data = await state.get_data()
            database.create_profile(user_id, data["name"], data["referral_id"])
            database.get_profile(user_id)
            # db.update_ref_amount(data["referral_id"])
            await message.answer(f"Great! You have used the referral code {data['referral_id']} to sign up.")
            await state.clear()
        else:
            await message.reply("You are already registered.")
    else:
        await message.reply("Invalid referral code. Please /start again.")

# change_profile = 



async def process_greetings(message: Message) -> bool:
    if is_greeting_word(message.text.lower()):
        # Если текст является приветствием, отправляем приветственный ответ
        await message.answer(f"👋 {greetings_reply()}", reply_markup=kb.menu, parse_mode="HTML")
        return True  # Возвращаем True, если приветствие обработано
    return False  # Если это не приветствие, возвращаем False
from app.handlers.commands import find_partner_handler

async def process_text_commands(message: Message):
    user_id = message.from_user.id
    print(1)
    if message.text == '➕ Add':
        print("add")
        await handle_add_command(user_id, bot)
        return True
    elif message.text == '🔍 Find a partner':
        print(2)
        await find_partner_handler(user_id, message)
        return True
    elif message.text == '🚫 Disconnect 🚫':
        await handle_disconnect(message)
        return True
    elif message.text == '🚫 Stop searching':
        await stop_searching(user_id, message)
        return True
    elif message.text == "💋 Kiss":
        await kiss_button_handler(message)
        return True
    # elif message.text == '💬 T or D? 💋':
    #     await message.answer("<b>You can ask something you find interesting from the partner. Remember, you have to follow the rules.\n\n Tips which are sent here are frozen for 72h.</b>", reply_markup=kb.trd, parse_mode="HTML")
    #     return True
    
    # Если команда не найдена, возвращаем False
    return False


async def handle_add_command(user_id, message):
    chat = database.get_chat(user_id)
    print(12345)
    print(user_id)
    print(12345)
    print(chat)
    if chat:
        partner_id = chat[1]
        await add_friend_request(user_id, partner_id, message)


async def add_friend_request(user_id, partner_id, message: Message):
    
    # Получаем список друзей пользователя
    frns_list = database.get_frns_list(user_id) or []  # если None, заменяем на пустой список

    # Считаем количество друзей, исключая None
    frns_count = len([f for f in frns_list if f is not None])
    print(f"print(frns_count), {frns_count}")  # исправлен вывод количества друзей

    user_name = database.get_profile(user_id)[1]

    # Проверяем, что у пользователя меньше 5 друзей
    if frns_count < 5:
        print(1)
        # Проверяем, есть ли уже этот партнер в списке друзей
        if partner_id in frns_list:
            print(3)
            await bot.send_message(user_id, "<b>You are already friends with this partner!</b>", parse_mode="HTML")
            return
        else:
            print(4)
            # Создаем кнопки для партнера, чтобы он принял или отклонил запрос
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Accept", callback_data=f'accept_friend_{user_id}'),
                 InlineKeyboardButton(text="❌ Dismiss", callback_data=f'reject_friend_{user_id}')]
            ])
            # Отправляем сообщение партнеру
            await bot.send_message(partner_id, f"<b>User {user_name} wants to add you.</b>", parse_mode="HTML", reply_markup=buttons)
            # Сообщаем пользователю, что запрос отправлен
            await bot.send_message(user_id, "<b>Request is sent!</b>", parse_mode="HTML")
    else:
        # Если у пользователя максимальное количество друзей
        await bot.send_message(user_id, "<b>You have the maximum number of friends now.</b>", parse_mode="HTML")


@msg_router.callback_query(lambda c: c.data.startswith('accept_friend_') or c.data.startswith('reject_friend_'))
async def handle_friendship_response(callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id  # Текущий пользователь, который нажал на кнопку
    request_user_id = int(data.split('_')[-1])  # Пользователь, который отправил запрос на дружбу

    if 'accept_friend' in data:
        # Логика для принятия запроса
        database.add_frn(user_id, request_user_id)
        database.add_frn(request_user_id, user_id)
        await callback_query.message.edit_text(f"<b>Request accepted! Now you are the friends with {request_user_id}.</b>", parse_mode="HTML")
       
        await bot.send_message(request_user_id, f"<b>{user_id} just added you to the friends.</b>", parse_mode="HTML", reply_markup=kb.chat_menu)
    elif 'reject_friend' in data:
        # Логика для отклонения запроса
        await callback_query.message.edit_text("<b>Запрос отклонен.</b>", parse_mode="HTML")

add_frn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Yes", callback_data="add_frn")]
    ])
      

@msg_router.message(F.data == "add_frn")
async def friend_adding(callback: CallbackQuery):
    
    
    user_id = callback.from_user.id
    partner_id = database.get_chat(user_id)
    frns_list = database.get_friends_list(user_id)
    frns_count = len(frns_list)
    cant = "You can't add more."
    can = "Are you sure you want to add?"
    database.send_friendship_request(user_id,partner_id, )

    text = can if frns_count < MAX_FREINDS else cant
    callback.message.answer(f"<b>You have {frns_count} friends</b>", text, reply_markup=add_frn, parse_mode="HTML")
    database.add_frn(user_id, partner_id)
    pass





async def find_partner(user_id: int, message: Message):
    partner_id = database.get_queue()
    if not database.create_chat(user_id, partner_id):
        database.add_queue(user_id)
        await message.answer("<b>Finding a partner...</b>", reply_markup=kb.stop, parse_mode="HTML")
    else:
        database.delete_queue(user_id)
        database.delete_queue(partner_id)
        await message.answer("<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")
        await bot.send_message(partner_id, "<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")


async def handle_disconnect(message: Message):
    user_id = message.from_user.id
    chat = database.get_chat(user_id)

    if chat:
        partner_id = chat[1]
        message_count = user_message_count.get(user_id, 0)
        
        # Завершение чата и сохранение логов
        created_time = None
        try:
            created = database.get_chat_created_time(user_id)
            created_time = created[0]
        except Exception as e:
            created_time = None

        ended_time = get_current_time()

        # Сохранение логов чата в базу данных
        database.create_chat_logs(message_count, created_time, ended_time, user_id, partner_id)
        
        # Отправка уведомлений об отключении
        await message.answer("<b>You have been disconnected from the chat!</b>", reply_markup=kb.menu, parse_mode="HTML")
        await message.answer("<b>Please rate the previous user, or skip if you prefer.</b>", reply_markup=kb.rate_new, parse_mode="HTML")
        await bot.send_message(partner_id, "<b>Your partner has disconnected from the chat!</b>", reply_markup=kb.menu, parse_mode="HTML")
        await bot.send_message(partner_id, "<b>Please rate the previous user, or skip if you prefer.</b>", reply_markup=kb.rate_new, parse_mode="HTML")

        # Очистка данных чата
        database.delete_chat(user_id)
        user_message_count.pop(user_id, None)  # Сброс счётчика сообщений
    else:
        await message.answer("<b>You are not connected to any chat!</b>", parse_mode="HTML", reply_markup=kb.menu)

async def stop_searching(user_id: int, message: Message):
    # Удаление пользователя из очереди поиска
    database.delete_queue(user_id)
    
    # Отправка сообщения пользователю
    await message.answer("<b>Search stopped!</b>", reply_markup=kb.menu, parse_mode="HTML")

    # Сброс счётчика сообщений, если такой был
    user_message_count.pop(user_id, None)  # Сброс счётчика сообщений


async def forward_message_to_partner(user_id: int, message: Message):
    chat = database.get_chat(user_id)

    if chat:
        partner_id = chat[1]
        text = message.text

        # Отправка сообщения партнёру
        await bot.send_message(partner_id, text)
    else:
        await message.answer("<b>You are not connected to any chat!</b>", parse_mode="HTML", reply_markup=kb.menu)


async def process_message_count(user_id: int, user_message_count: dict) -> dict:
    # Проверяем, есть ли уже счётчик сообщений для данного пользователя
    if user_id not in user_message_count:
        user_message_count[user_id] = 0  # Инициализируем счётчик, если его ещё нет

    # Возвращаем обновлённый словарь с количеством сообщений
    return user_message_count






@msg_router.message(F.text == "💋 Kiss")
async def kiss_button_handler(message: types.Message):

    amount = 1
    user_id = message.from_user.id
    chat = database.get_chat(user_id)
    if chat:
        partner_id = chat[1]
        
        current_balance = database.get_balance(user_id)
        
        if current_balance >= amount:
            new_sender_balance = current_balance - amount
            database.update_balance(user_id, new_sender_balance)
            
            # Получите баланс партнера и обновите его
            partner_balance = database.get_balance(partner_id)
            new_receiver_balance = partner_balance + amount
            database.update_balance(partner_id, new_receiver_balance)
            
            # Получите обновленный баланс партнера
            partner_balance = database.get_balance(partner_id)

            partner = database.get_profile(partner_id)
            user = database.get_profile(user_id)
            new_balance = database.get_balance(user_id)
            # Отправьте уведомление партнеру
            await bot.send_sticker(partner_id, sticker_pack[3])
            await bot.send_message(partner_id, f"<b>You received a tip of {amount} from user {user[1]}. Now you have {partner_balance}.</b>", parse_mode="HTML")
            await message.answer(f"<b>Success! You tipped {amount} to user {partner[1]}.\n\nYou have {new_balance} left</b>", reply_markup=kb.balance_bot, parse_mode="HTML")

        else:
            await message.answer("<b>You don't have enough tokens</b>!", parse_mode="HTML", reply_markup=kb.balance_bot)



@msg_router.message(F.text)
async def bot_message(message: Message, state: FSMContext):
    # Проверяем текущее состояние FSM (Finite State Machine)
    current_state = await state.get_state()
    print(current_state)
    print(ProfileMaking.referral_id)

    if current_state == ProfileMaking.referral_id:
        # Если пользователь в состоянии ввода реферального кода, ничего не делаем здесь
        return
    
    if message.chat.type != 'private':
        await message.answer("<b>Bot works only in private chat!</b>")
        return
    
    user_id = message.from_user.id
    # Обработка текстовых команд (кнопок)
    if await process_text_commands(message):
        return
    
    chat_exists = database.chat_exists(user_id)

    if chat_exists:
        # Если чат существует, пересылаем сообщение партнеру
        await forward_message_to_partner(user_id, message)
    else:
        # Если чата нет, проверяем приветствие
        if await process_greetings(message):
            return
        
        # Проверка на запрещённый контент
        warning = await check_for_prohibited_content(message.text, user_id)
        if warning:
            await message.answer(warning)
            return
        
        # Если приветствия нет и не было запрещенного контента, отправляем unknown текст
        await message.answer(f"❓ {unknown_text_reply()}", parse_mode="HTML")



@msg_router.message(F.content_type.in_({'voice', 'photo', 'document', 'video', 'sticker', 'audio', 'video_note'}))
async def media_handler(message: Message):
    chat = database.get_chat(message.chat.id)
    if chat:
        if message.content_type == 'voice':
            await bot.send_voice(chat[1], message.voice.file_id)
        elif message.content_type == 'photo':
            await bot.send_photo(chat[1], message.photo[-1].file_id)
        # elif message.content_type == 'document':
        #     await bot.send_document(chat[1], message.document.file_id)
        # elif message.content_type == 'video':
        #     await bot.send_video(chat[1], message.video.file_id)
        # elif message.content_type == 'sticker':
        #     await bot.send_sticker(chat[1], message.sticker.file_id)
        # elif message.content_type == 'audio':
        #     await bot.send_audio(chat[1], message.audio.file_id)
        elif message.content_type == 'video_note':  # Проверяем, если это круговое видео
            await bot.send_video_note(chat[1], message.video_note.file_id)
        else:
            reply =  "<b>Oops! My circuits don't know how to process this type of file. Try again or press /help!</b>"
            await message.answer(reply, parse_mode="HTML")
    else:
        if message.content_type == 'sticker':
            reply = random.choice(sticker_responses)
        elif message.content_type == 'photo':
            reply =  random.choice(photo_responses)
        elif message.content_type ==  'video':
            reply =  random.choice(video_responses)
        elif message.content_type ==  'document':
            reply =  random.choice(document_responses)
        elif message.content_type == 'video_note':  # Обрабатываем случай для круговых видео
            reply = "Ого, это круговое видео!"
        else:
            reply =  "<b>Oops! My circuits don't know how to process this type of file. Try again or press /help!</b>"
        await message.answer(reply, parse_mode="HTML")



def get_last_fren_number(frns_list):
    if frns_list[1]:
        if frns_list[2]:
            if frns_list[3]:
                if frns_list[4]:
                    if frns_list[5]:
                        return 5
                    else: 
                        return 4
                else:
                    return 3
            else:
                return 2
        else:
            return 1       
    else:
        return 0






# Handle callback for entering referral code
@msg_router.callback_query(lambda c: c.data == "enter_referral_code")
async def enter_referral_code_callback(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Please send your referral code.")
    await state.set_state(ProfileMaking.referral_id)
    print(1)
    await callback_query.answer()

# Handle referral code submission
@msg_router.message(ProfileMaking.referral_id)
async def handle_referral_code(message: Message, state: FSMContext):
    user_id = message.from_user.id
    referral_code = message.text.strip()
    print(2)
    if database.user_exists(referral_code):
        if not database.user_exists(user_id):
            user_name = message.from_user.full_name
            await state.set_state(ProfileMaking.name)
            await state.update_data(name=user_name)
            await state.set_state(ProfileMaking.gender)
            await state.update_data(gender="Male")
            await state.update_data(referral_id=referral_code)
            data = await state.get_data()
            database.create_profile(user_id, data["name"], data["referral_id"])
            database.get_profile(user_id)
            # db.update_ref_amount(data["referral_id"])
            await message.answer(f"Great! You have used the referral code {data['referral_id']} to sign up.")
            await state.clear()
        else:
            await message.answer("You are already registered.")
    else:
        await message.reply("Invalid referral code. Please try again.")

# change_profile = 
