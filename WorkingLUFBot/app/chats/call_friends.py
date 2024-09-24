from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from db.database import Database 
import app.keyboards.keyboards as kb 
from config import bot, dp, TOKEN, emoji_list
import time

refs = 2
call_router = Router()
database = Database()
user_last_request_time = {}

# Sample friends list with unique IDs
# friends_list = [
#     {'name': 'J', 'id': 41960650},
#     {'name': 'Po', 'id': 845451513},
# ]

# keyboard = InlineKeyboardMarkup([
#     [InlineKeyboardButton]])

import random
# Step 2: Create Inline Keyboard for Friends List
# Step 2: Create Inline Keyboard for Friends List
emojis = [
    "😀", "😂", "😍", "😎", "🤔", "🤯", "🥳", "🤩", "😜", "😝",
    "😛", "😶", "😸", "😻", "😽", "🙀", "😾", "😹", "😺", "😿",
    "🤗", "🤤", "😴", "😷", "🤒", "🤕", "🤢", "🤧", "🤮", "🥵",
    "🥶", "🥴", "😵", "😲", "😳", "🥺", "😢", "😭", "😤", "😠",
    "😡", "🤬", "😈", "👿", "💀", "☠️", "👻", "👽", "💩", "🤡",
    "👀", "👁️", "👅", "👄", "💋", "💌", "💖", "💗", "💓", "💔",
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍", "🤎",
    "🌈", "🌟", "✨", "🔥", "💥", "🌪️", "🌊", "🌋", "🎃", "🎄",
    "🎆", "🎇", "🎉", "🎊", "🎈", "🎉", "🎀", "🎁", "🎗️", "🏆",
    "🎽", "🎿", "🎯", "🎱", "🏅", "🥇", "🥈", "🥉", "🏆", "🎽"
]

def get_emoji_for_user(user_id):
    import hashlib
    
    # Хешируем user_id и преобразуем в целое число
    hash_object = hashlib.md5(str(user_id).encode())
    hash_hex = hash_object.hexdigest()
    
    # Преобразуем первые 2 символа хеша в целое число
    index = int(hash_hex[:2], 16)
    
    # Находим индекс в пределах длины списка emojis
    emoji_index = index % len(emojis)
    
    return emojis[emoji_index]

def get_user_emoji(number):

    return emoji_list[number]

async def inline_friends_keyboard(user_id):
    keyboard = InlineKeyboardBuilder()
    seen_ids = set()

    # Fetch the user's friends list from the database
    friends_list = database.get_frns_list(user_id)
    
    if friends_list:
        for friend_id in friends_list:
            # If the friend ID exists (is not None) and hasn't been seen already
            if friend_id and friend_id not in seen_ids:
                database.create_frns_list(user_id)
                friend = database.get_profile(friend_id)
                print(friend)
                name = friend[1]
                seen_ids.add(friend_id)
                emoji = get_emoji_for_user(friend_id)
                # emoji = get_user_emoji(random.randrange(0,5))
                # Fetch friend's name (assuming you have a way to get the friend's name)
                friend_name = f"{emoji} {name}"  # Replace with actual name retrieval if possible
                # Add the friend to the inline keyboard
                keyboard.add(InlineKeyboardButton(text=friend_name, callback_data=f"select_friend:{friend_id}"))
                print(f"select_friend:{friend_id}")
    else:
        # If no friends found, add a message in the keyboard
        keyboard.add(InlineKeyboardButton(text="No friends yet", callback_data="no_friends"))
    
    # Adjust the buttons layout and return the markup
    return keyboard.adjust(3).as_markup()

async def notify_friend(friend_id, user_name, request_markup):
    try:
        await bot.send_message(friend_id, f"<b>User {user_name} wants to chat with you. Do you accept?</b>", reply_markup=request_markup, parse_mode="HTML")
        return True
    except Exception as e:
        print(f"Error sending request to friend {friend_id}: {e}")
        return False

@call_router.callback_query(F.data.startswith("select_friend:"))
async def friend_selected(call: CallbackQuery):
    friend_id = call.data.split(":")[1]
    user_id = call.from_user.id
    user_name = call.from_user.full_name
    current_time = time.time()

    print(f"Callback received: {call.data}")
    print(f"User ID: {user_id}, Friend ID: {friend_id}")

    user_last_request_time[user_id] = current_time

    request_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Answer", callback_data=f"answer_request:{user_id}:{friend_id}")],
        [InlineKeyboardButton(text="Dismiss", callback_data=f"dismiss_request:{user_id}:{friend_id}")]
    ])
    cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Cancel Request", callback_data=f"cancel_request:{user_id}:{friend_id}")]
    ])

    # Notify the friend about the request
    success = await notify_friend(friend_id, user_name, request_markup)
    if success:
        await call.message.answer(f"Your request has been sent to the friend with ID {friend_id}.", reply_markup=cancel_markup)
    else:
        await call.message.answer("Failed to send the request. The friend might not be available.")
    
    await call.answer()

# @fren_router.callback_query(F.data.startswith("select_friend:"))
# async def friend_selected(call: CallbackQuery):
#     friend_id = call.data.split(":")[1]
#     user_id = call.from_user.id
#     current_time = time.time()

#     print(f"Callback received: {call.data}")
#     print(f"User ID: {user_id}, Friend ID: {friend_id}")

#     # Update last request time
#     user_last_request_time[user_id] = current_time
#     print(1)
#     # Notify the friend about the request
#     try:
#         print(2)
#         request_markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Answer", callback_data=f"answer_request:{user_id}:{friend_id}")],
#             [InlineKeyboardButton(text="Dismiss", callback_data=f"dismiss_request:{user_id}:{friend_id}")]
#         ])
#         cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Cancel Request", callback_data=f"cancel_request:{user_id}:{friend_id}")]
#         ])
#         print(friend_id)
#         await bot.send_message(friend_id, f"User {call.from_user.full_name} wants to chat with you. Do you accept?", reply_markup=request_markup)
#         await call.message.answer(f"Your request has been sent to the friend with ID {friend_id}.", reply_markup=cancel_markup)
#     except Exception as e:
#         print(f"Error sending request to friend {friend_id}: {e}")
#         await call.message.answer("Failed to send the request. The friend might not be available.")

#     await call.answer()


# Step 5: Handle Answer Request
@call_router.callback_query(F.data.startswith("answer_request:"))
async def answer_request(call: CallbackQuery):
    _, requester_id, friend_id = call.data.split(":")
    requester_id = int(requester_id)
    friend_id = int(friend_id)


    # Logic to create a chat between the users
    database.create_chat(requester_id, friend_id)

    # Notify both users about the connection
    await bot.send_message(requester_id, "<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")
    await bot.send_message(friend_id, "<b>You are connected to the chat!</b>", reply_markup=kb.chat_menu, parse_mode="HTML")

    await call.message.answer("You have connected with the requester!")
    await call.answer()

# Step 6: Handle Dismiss Request
@call_router.callback_query(F.data.startswith("dismiss_request:"))
async def dismiss_request(call: CallbackQuery):
    _, requester_id, friend_id = call.data.split(":")
    requester_id = int(requester_id)

    # Notify the requester about the dismissal
    await bot.send_message(requester_id, "Your chat request has been dismissed by the recipient.")
    await call.message.answer("You have dismissed the request.")
    await call.answer()

# Step 7: Handle Cancel Request
@call_router.callback_query(F.data.startswith("cancel_request:"))
async def cancel_request(call: CallbackQuery):
    _, requester_id, friend_id = call.data.split(":")
    requester_id = int(requester_id)
    friend_id = int(friend_id)

    # Notify the recipient about the cancellation
    await bot.send_message(friend_id, "The chat request has been canceled by the requester.")
    
    # Notify the requester about the cancellation
    await bot.send_message(requester_id, "You have canceled the chat request.")
    
    # Optionally, you might want to delete the request from the database or memory here

    await call.message.edit_reply_markup()  # Remove the cancel button from the request message
    await call.answer()

# Step 8: Handle Back to Menu
@call_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    # Logic to return to the main menu
    await call.message.answer("Returning to the main menu.", reply_markup=kb.menu)
    await call.answer()


# @fren_router.message(F.text == "Referals")
# async def info_handler(message: Message, state: FSMContext):
#     await message.answer(f"You have {refs}", reply_markup=kb.more)
