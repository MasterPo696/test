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
btn_router = Router()

class Profile(StatesGroup):
    user_id = State()
    gender = State()
    referral_id = State()


    # Define states
class ProfileMaking(StatesGroup):
    name = State()
    gender = State()
    searching_for = State()
    hetero = State()
    photo = State()
    report = State()
    referral_id = State()




@btn_router.callback_query(lambda c: c.data in ["male1", "male2", "female1","female2"])
async def rules_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    gender = "male" if callback.data == "male1" else "female"
    await state.update_data()
    db.update_gender(user_id, gender)
    # await state.get_state(ProfileCreation.picture)
    await callback.message.answer("<b>All right!</b>", parse_mode="HTML")
    # await state.update_data(picture =)

# Handle "Profile" command
@btn_router.message(F.text == "👤 Profile")
async def profile_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.full_name

    profile = db.get_profile(user_id)
    gender = db.get_gender(user_id)

    if profile:
            
                await bot.send_sticker(user_id, sticker_pack[1])

                amount = 2
                
                intersted_in = profile[6]
                have_message = f"You have {amount} me$$ages."
                no_messages = "Oops."

                refs_amount = 10
                name = profile[1]
                balance = profile[4]
                diamonds = 2
                intersted_in = profile[6]
                gender_key = "F" if intersted_in == 'female' else "M"
                lover_key = "F" if intersted_in == 'female' else "M"
                frens = "lufer" if refs_amount == 1 else "lufers"


                # await message.answer(
                #         f"<b>🚀 Profile Overview for {name}:</b>\n\n"
                #         f"<b>🌀 Gender:</b> {gender_key}\n"
                #         f"<b>💓 Goal:</b> {lover_key} /flow😉\n\n"
                #         f"<b>💸 Your Balance:</b>\n"
                #         f"🔹 {balance} tks\n"
                #         f"🔸 {diamonds} luf\n\n"

                #         f"🏆 <b>Referral bonus:</b> {refs_amount}\n"
                #         f"💬 <b>Messages:</b> {1}\n\n"
                #         f"<a href='link'>💥 Get more LUFs!</a>", 
                #         parse_mode="HTML", reply_markup=kb.balance_bot)
                        
                time = 5
                await message.answer(
                    f"<b>Here is your profile, {profile[1]}.</b>\n\n"
                    f"Your sex is <b>{gender_key}</b>\n" 
                    f"You are into <b>{lover_key}</b>\n\n"
                    f"Blind zone's on in <b>{time}h</b>\n"
                    f"Balance is <b>{balance} tokens</b>\n\n"     
                    f"<b>Get more here</b>.", parse_mode="HTML", reply_markup=kb.balance_bot
                )
    if gender == None:
        await message.answer("<b>Choose Your gender to update data.</b>",parse_mode="HTML",  reply_markup=kb.mf1)
                # Fetch the user's level from the experience table



@btn_router.callback_query(F.data == 'loading_pic')
async def rules_handler(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    await state.get_state(ProfileCreation.picture)
    await callback.message.answer("<b>Please send the picture of yours!</b>", parse_mode="HTML")
    # await state.update_data(picture =)

@btn_router.message(ProfileCreation.picture)
async def rules_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if message.content_type == 'photo':
        pass
    else:
        message.answer("<b>Please send the picture of yours!</b>", parse_mode="HTML")


    # await state.get_state(ProfileCreation.picture)
    # await state.update_data(picture =)
    

@btn_router.callback_query(F.data == 'rules_agree')
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





# Step 3: Handle "👩‍❤️‍👨 Lovers" message to show the friends list
@btn_router.message(F.text == "👩‍❤️‍👨 Lovers")
async def show_friends(message: Message):
    user_id = message.from_user.id
    chat = db.chat_exists(user_id)
    if chat == False:
        db.create_frns_list(user_id)
        frn_list = db.get_frns_list(user_id)
        print(frn_list)

        if len(frn_list) > 0:
            # Generate the keyboard with the list of friends
            keyboard = await inline_friends_keyboard(user_id)

            # Send a message with the inline keyboard to the user
            await message.answer(f"<b>Here is your friend list:</b>", reply_markup=keyboard, parse_mode="HTML")
        else: 
            await message.answer(f"<b>You don't have any friends.</b>", reply_markup=kb.menu, parse_mode="HTML")
    else:
        await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)      



@btn_router.message(F.text == "🆕 New")
async def new_futures_handler(message: types.Message):
    user_id = message.from_user.id
    chat = db.chat_exists(user_id)
    if chat == False:
        await message.answer(
        f"<b>⬇️ <u>Futures Updates Coming:</u> ⬇️</b>\n\n"
        f"<b>📅 Q4 2024: Limited Presale for Early Users</b>\n"
        f"Anyone who is in the close beta will be able to take a part in sale and receive 'voting' coins, which won’t be minted again. 💎\n\n"
        f"<b>🚀 Q1 2025: Farming Starts</b>\n"
        f"Farming will commence, allowing users to earn coins that can be spent later. 🌾💰\n\n"
        f"<b>🎉 Q2 2025: Second Presale and Referrals Counting Ends</b>\n"
        f"Referrals and coin holders will receive bonuses, and then the referral system will conclude. 🎁📈\n\n"
        f"<b>🎁 Q3 2025: Airdrop for Holders</b>\n"
        f"A massive airdrop for all users, with $ and bonuses. 🚀💸\n\n"
        f"<b>Don't forget to follow the sources, to be in #LUF.</b>",
        reply_markup=kb.more2, parse_mode="HTML"
        )
    else:
        await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)      


@btn_router.message(F.text =="Launge")
async def launch_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    chat = db.chat_exists(user_id)
    if chat == False:
        user_lvl = await user_level(user_id, message)
        
        if user_lvl is not None and user_lvl > 5:
            await bot.send_sticker(user_id, sticker_pack[3])
            await message.answer("<b>You are welcome</b>.", reply_markup=kb.launch_keyboard)
        elif user_lvl < 2:
            await bot.send_sticker(user_id, sticker_pack[0])
            await message.answer("<b>Your level is too low</b>.")
            # Отправляем стикер пользователю
        elif user_lvl == 3:
            await bot.send_sticker(user_id, sticker_pack[1])
            await message.answer("<b>Your level is too low</b>.")
            # Отправляем стикер пользователю
        elif user_lvl == 4:
            await bot.send_sticker(user_id, sticker_pack[3])
            await message.answer("<b>Your level is too low</b>.")
            # Отправляем стикер пользователю
    else:
          await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)
        



"Hi. `Press me!`!"


@btn_router.message(F.text == "ℹ️ Info")
async def info_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    chat = db.chat_exists(user_id)
    if chat == False:
        await bot.send_sticker(user_id, sticker_pack[1])
        
        
        await message.answer("<b>🚀🌟 Hello, LUFers!🌟🚀</b>\n"
            "We are excited to launch LUF, a community built on love and connection. 🥰\n\n"
        
            "<b>What is LUF?</b> 😻\n"
            "LUF is more than a project—it’s a journey that started long ago. Today, we plant the seed of love, ready to watch it grow. 🌱🌺\n\n"
            
            "<b>Where are we?</b>\n"
            "Though we live on different continents, we are united as LUFers. Together, we are stronger. 🌍\n\n"
            
        " <b>Why LUF?</b>\n"
            "Our mission is to create a lifestyle that lifts and empowers us, bringing us closer to the stars. ✨\n\n"
            
        " 🌟 <b>Join the movement now!</b> Launch the bot: <a href='https://t.me/LUFChatBot'>LUF Bot</a> ⚡\n\n"
            
            "Be part of the <b>#LUF</b> and the future we’re building. 💖", parse_mode="HTML", reply_markup=kb.more
        )
    else:
          await message.answer(f"👋<b> You are in a chat!</b>", parse_mode="HTML", reply_markup=kb.chat_menu)      