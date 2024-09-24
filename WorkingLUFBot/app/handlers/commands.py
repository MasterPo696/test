import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.database import Database
from config import TOKEN, ETH_WALLET, sticker_pack
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
router = Router()

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  

referral_code = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data='yes'),InlineKeyboardButton(text="No", callback_data='no')]])


class User(StatesGroup):
    user_id = State()
    name = State()
    gender = State()
    looking_for = State()
    level = State()
    picture = State()
    referral_id = State()
    code = State()
    verif =State ()


gender = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="M", callback_data='m'),InlineKeyboardButton(text="F", callback_data='f')]])





# @router.callback_query(lambda c: c.data in ["m", "f"])
# async def handle_invite_button(callback: CallbackQuery, state: FSMContext):
#     result = "m" if callback.data == "m" else "f"
#     if result == "m":
#         await callback.message.answer(f"<b>👋 Welcome, buddy!</b>", parse_mode="HTML", reply_markup=kb.menu)
#         # await state.update_data(User.gender)
#     else:
#         await callback.message.answer(f"<b>👋 Welcome, cutie!</b>", parse_mode="HTML", reply_markup=kb.menu)
#     await state.update_data(gender=result)
#     # await state.get_data
#     data = await state.get_data()
#     print(data)
#     user_id = callback.from_user.id
#     user_name = callback.from_user.full_name
#     gender = data['gender']
#     referral_id_data = data['referral_id']
#     print(referral_id_data)
#     print(data)
#     db.create_profile(user_id, user_name, gender, referral_id_data)
#     # await state.clear()
#     await callback.message.answer(f"<b>👋 Now you can use the app!</b>", parse_mode="HTML")
    
    
# @router.callback_query(lambda c: c.data in ["male2", "female2"])
# async def handle_invite_button(callback: CallbackQuery, state: FSMContext):
#     result = "male" if callback.data == "male2" else "female"
#     user_id = callback.message.from_user.id
#     await callback.message.answer(f"<b>👋 You chose {result}</b>", parse_mode="HTML", reply_markup=kb.menu)
#     # await state.get_state(User.looking_for)
#     # await state.update_data(looking_for=result)
#     print(db.update_interested_in(user_id, result))
#     print(db.get_looking_for(user_id))
#     await callback.message.answer(f"<b>👋 Good luck with {result}</b>", parse_mode="HTML")
    


# @router.message(User.code)
# async def handle_code(message: Message, state: FSMContext):
#     print("andle_code")
#     referral_id = message.text
#     result = db.get_profile(referral_id)
#     verif = True if result else False
#     await state.update_data(referral_id=referral_id,verif=verif)
#     # await message.answer(f"👋<b> Checking...</b>", reply_markup=referral_code, parse_mode="HTML")
#     if verif:
#         await message.answer(f"<b>Allright! Now choose here.</b>", reply_markup=gender, parse_mode="HTML")
#     else:
#         await message.answer(f"<b>You can't go into the bot yet.\n\n Try again? /start</b>", parse_mode="HTML")
#         await state.clear()





# @router.callback_query(lambda c: c.data in ["yes", "no"])
# async def handle_invite_button(callback: CallbackQuery, state: FSMContext):
#     print("andle_code")
#     result = True if callback.data == "yes" else False
#     if result:
#         await callback.message.answer(f"<b>Print it please</b>", parse_mode="HTML")
#         await state.set_state(User.code)
#     else:
#         await callback.message.answer(f"<b>This app can't used by you yet.\n\n Try again? /start</b>", parse_mode="HTML")
#         # await state.clear()
import random 
from texts.text_generation import welcome_text_list

# Handle /start command
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    
    # await state.clear()
    user_id = message.from_user.id
    chat = db.chat_exists(user_id)
    if chat == False:

        # user_name = message.from_user.full_name
        profile = db.get_profile(user_id)
        data = await state.get_data()
        verif = data.get('verif')
        if profile:
            await message.answer(f"👋 {welcome_text_list[random.randrange(0,7)]}", parse_mode="HTML", reply_markup=kb.menu)
        elif profile == None or verif == True:
            args = message.text.split()[1:] if len(message.text.split()) > 1 else None
            if args == None and profile == None:
                    await message.answer(f"<b>Do you have the invition?</b>", reply_markup=referral_code, parse_mode="HTML")
            if args:
                referral_id = args[0]
                print(referral_id)
                result = db.get_profile(referral_id)
                # await state.get_state(User.referral_id)
                # await state.get_state(User.referral_id)
                await state.update_data(referral_id=referral_id)
                data = await state.get_data()
                referral_id_data = data['referral_id']
                print(referral_id_data)
                attempts_count = 1

                if result != None:
                    await message.answer(f"<b>Thank you, ur friend is cool!</b>",reply_markup=gender, parse_mode="HTML")

                    # await state.clear()
                else:
                    await message.answer(f"<b>This app can't used by you yet.</b>")
                    return
                
                # db.update_ref_amount(data["referral_id"])
                await bot.send_sticker(user_id, sticker_pack[0])
            else:
                print("Goooo")
        await state.clear()
    else:
        await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)



    # async def find_partner(user_id: int, message: Message):
    #     partner_id = database.get_queue()
    #     if not database.create_chat(user_id, partner_id):
    #         database.add_queue(user_id)
    #         await message.answer("<b>Finding a partner...</b>", reply_markup=kb.stop, parse_mode="HTML")
    #     else:
    #         database.delete_queue(user_id)
    #         database.delete_queue(partner_id)
    #         await message.answer("<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")
    #     
    #     await bot.send_message(partner_id, "<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")


    @router.callback_query(F.data == 'rules_agree')
    async def rules_handler(callback: CallbackQuery):
        user_id = callback.from_user.id
        
        
        # Update the database to record the agreement
        result = db.rules_agree(user_id, True)
        
        # Modify the inline keyboard button text
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Rules Agreed", callback_data='rules_agreed')]
        ])
        
        # Edit the message text and update the inline keyboard
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text="<b>You Successfully Agreed with the Rules</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    print(result)
    return result


@router.message(F.text == '🔍 Find a partner' )
async def find_partner_handler(message: Message, bot: Bot):
    user_id = message.from_user.id
    exist = db.get_profile(user_id)
    interested_in = db.get_looking_for(user_id)
    gender = db.get_gender(user_id)
    chat = db.chat_exists(user_id)
    print(chat)
    if chat == False:
        if exist:
            sex = gender[0]
            if interested_in:
                looking_for = interested_in[0]
                if (await check_user_in_channel(bot, user_id) == 0):
                    rules = exist[11]
                    if rules == 1:
                        partner = db.get_queue()
                        if partner and partner != user_id:
                            if db.create_chat(user_id, partner):
                                db.delete_queue(user_id)
                                db.delete_queue(partner)
                                
                                await message.answer("<b>You are connected to the chat!</b> ", reply_markup=kb.chat_menu, parse_mode="HTML")
                                
                                await bot.send_message(partner, "<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")
                            else:
                                await message.answer("<b>An error occurred while creating the chat</b>.")
                        else:
                            db.add_queue(user_id)                           
                            await message.answer("<b>Finding a partner...</b>", reply_markup=kb.stop, parse_mode="HTML")
                    else:
                        await message.answer(
                            "<b>Before we begin, please carefully read the chat rules!</b>\n\n"
                            "1. <i>Respect others.</i> Avoid topics that are hurtful, offensive, or morally questionable.\n"
                            "2. <i>Stay safe.</i> Be cautious when sharing personal information—trust should be earned, not given easily.\n"
                            "3. <i>Be mindful.</i> Engage in meaningful and respectful conversations.\n\n"
                            "<b>By clicking 'OK,' you agree to follow these rules.</b>",
                            reply_markup=kb.rules,
                            parse_mode="HTML"
                        )
                else:
                    await message.answer('<b>You have to follow the Channel to use the Bot.</b>', reply_markup=kb.more, parse_mode="HTML")
    
            else:
                await message.answer("<b>You need to choose who you are looking for. \nFemale</b> or <b>Male</b>", reply_markup=kb.mf2, parse_mode="HTML")
        else:
            await message.answer("<b>You don't have a profile, press /start</b>", parse_mode="HTML")
    else:
        await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)      


@router.message(Command("help"))
async def start(message: Message):
     
    start_text = "<b>Bot Commands:\n\n🔹 to /start the bot\n🔹 if you need /help\n🔹 give a /kiss\n🔹 my /referral\n\n❓ <b>Houstom, we have a problem.</b>"
    await message.answer(start_text, parse_mode="HTML", reply_markup=kb.support)
    
    

# Пример отправки сообщения

# @router.message(Command("edit"))
# async def start(message: Message):
#     start_text = "<b>Here you can /edit info about urself.</b>"
#     await message.answer(start_text, parse_mode="HTML", reply_markup=kb.edit)


@router.message(Command('referral'))
async def send_referral_link(message: types.Message):
    user_id = message.from_user.id
     
    referral_link = f"<b>Here is your referral link:\n\nhttps://t.me/luf_reg_bot?start={user_id}</b>"
    await message.answer(f"<b>{referral_link}</b>", parse_mode="HTML", reply_markup=kb.menu)


# @router.message(F.text == "🆕 New Feature")
# async def new_futures_handler(message: types.Message):
#     await message.answer(
#     f"<b>⬇️ <u>Futures Updates Coming:</u> ⬇️</b>\n\n"
#     f"<b>📅 Q4 2024: Limited Presale for Early Users</b>\n"
#     f"Anyone who is in the close beta will be able to take a part in sale and receive 'voting' coins, which won’t be minted again. 💎\n\n"
#     f"<b>🚀 Q1 2025: Farming Starts</b>\n"
#     f"Farming will commence, allowing users to earn coins that can be spent later. 🌾💰\n\n"
#     f"<b>🎉 Q2 2025: Second Presale and Referrals Counting Ends</b>\n"
#     f"Referrals and coin holders will receive bonuses, and then the referral system will conclude. 🎁📈\n\n"
#     f"<b>🎁 Q3 2025: Airdrop for Holders</b>\n"
#     f"A massive airdrop for all users, with $ and bonuses. 🚀💸\n\n"
#     f"<b>Don't forget to follow the sources, to be in #LUF.</b>",
#     reply_markup=kb.more2, parse_mode="HTML"
# )


# @router.message(F.text =="Launge")
# async def launch_handler(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     user_lvl = await user_level(user_id, message)
     
#     if user_lvl is not None and user_lvl > 5:
#         await bot.send_sticker(user_id, sticker_pack[3])
#         await message.answer("<b>You are welcome</b>.", reply_markup=kb.launch_keyboard)
#     elif user_lvl < 2:
#         await bot.send_sticker(user_id, sticker_pack[0])
#         await message.answer("<b>Your level is too low</b>.")
#         # Отправляем стикер пользователю
#     elif user_lvl == 3:
#         await bot.send_sticker(user_id, sticker_pack[1])
#         await message.answer("<b>Your level is too low</b>.")
#         # Отправляем стикер пользователю
#     elif user_lvl == 4:
#         await bot.send_sticker(user_id, sticker_pack[3])
#         await message.answer("<b>Your level is too low</b>.")
#         # Отправляем стикер пользователю
        



# "Hi. `Press me!`!"


# @router.message(F.text == "ℹ️ Info")
# async def info_handler(message: Message, state: FSMContext):
#     user_id = message.from_user.id
    
#     await bot.send_sticker(user_id, sticker_pack[1])
     
    
#     await message.answer("<b>🚀🌟 Hello, LUFers!🌟🚀</b>\n"
#         "We are excited to launch LUF, a community built on love and connection. 🥰\n\n"
    
#         "<b>What is LUF?</b> 😻\n"
#         "LUF is more than a project—it’s a journey that started long ago. Today, we plant the seed of love, ready to watch it grow. 🌱🌺\n\n"
        
#         "<b>Where are we?</b>\n"
#         "Though we live on different continents, we are united as LUFers. Together, we are stronger. 🌍\n\n"
        
#        " <b>Why LUF?</b>\n"
#         "Our mission is to create a lifestyle that lifts and empowers us, bringing us closer to the stars. ✨\n\n"
        
#        " 🌟 <b>Join the movement now!</b> Launch the bot: <a href='https://t.me/LUFChatBot'>LUF Bot</a> ⚡\n\n"
        
#         "Be part of the <b>#LUF</b> and the future we’re building. 💖", parse_mode="HTML", reply_markup=kb.more
# )
    


@router.message(Command('kiss'))
async def tip_command_handler(message: types.Message):
    user_id = message.from_user.id
    text = F.text
    

    args = message.text.split()
    
    if len(args) > 1 and args[1].isdigit():
        amount = int(args[1])
    elif (text == "\kiss") and len(args)==1:
        amount = 1
    else:
        await message.answer(f'<b>Please use the command like as this: /kiss 10</b>', parse_mode="HTML")
        return
    chat = db.get_chat(user_id)
    
    if chat:
       
        partner_id = chat[1] # Пример: chat[1] может содержать ID партнера
    else:
        # Если не в чате, используйте last_partner_id из профиля пользователя
        profile = db.get_profile(user_id)
        partner_id = profile[5]
    if partner_id is None:
        await message.answer("<b>No partner found to send tip to.")
        return

    current_balance = db.get_balance(user_id)

    if current_balance >= amount:
        # Обновите баланс отправителя
        text 
        new_sender_balance = current_balance - amount
        db.update_balance(user_id, new_sender_balance)
        
        # Получите баланс партнера и обновите его
        partner_balance = db.get_balance(partner_id)
        new_receiver_balance = partner_balance + amount
        db.update_balance(partner_id, new_receiver_balance)
        
        # Получите обновленный баланс партнера
        partner_balance = db.get_balance(partner_id)

        partner = db.get_profile(partner_id)
        user = db.get_profile(user_id)
        new_balance = db.get_balance(user_id)
        # Отправьте уведомление партнеру
        await bot.send_sticker(partner_id, sticker_pack[3])
        await bot.send_message(partner_id, f'You received a tip of {amount} from user {user[1]}. Now you have {partner_balance}.')
        await message.answer(f"<b>Success! You tipped {amount} to user {partner[1]}.\n\nYou have {new_balance} left</b>", reply_markup=kb.balance_bot, parse_mode="HTML")
    else:
        await message.answer("<b>You don't have enough tokens</b>!", parse_mode="HTML", reply_markup=kb.balance_bot)

