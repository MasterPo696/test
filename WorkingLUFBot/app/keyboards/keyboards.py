from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  

rate_new = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Like", callback_data='like'),InlineKeyboardButton(text="Dislike", callback_data='dislike')],
    [InlineKeyboardButton(text='Report', callback_data='report')]])



# Handlers Keyboards
find = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Find a partner")]],
    resize_keyboard=True)

stop = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🚫 Stop searching")]],
    resize_keyboard=True)

trd = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="OK", callback_data='TrD_agree')]])

trd_yes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data='TrD_yes')]])

trd_partner_agree = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data='partner_agree'), InlineKeyboardButton(text="No", callback_data='parther_disagree')]])

# send_request_back = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="Send TrD", callback_data='send_trd')]])


price_yes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data='Price_yes'), InlineKeyboardButton(text="Stop", callback_data='stop')]])



send_trd_file = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Send TrD", callback_data='send_trd')]])


love_mode = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎀 Perfect Match"),KeyboardButton(text="🌘 Hiden LUF")]],
    resize_keyboard=False)

chat_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="💋 Kiss")],
                                          [KeyboardButton(text="🚫 Disconnect 🚫")]],resize_keyboard=True)


rules = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="OK", callback_data='rules_agree')]])


# menu = ReplyKeyboardMarkup(
#     keyboard=[
#         [KeyboardButton(text="Find a partner"), KeyboardButton(text="Profile")],
#         [KeyboardButton(text="Friends"), KeyboardButton(text="Balance")],
#         [KeyboardButton(text="Info"), KeyboardButton(text="New Feature")]  # New button added
#     ],
#     resize_keyboard=True
# )
loading_pic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Load Pic", callback_data='loading_pic')]])

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Find a partner"), KeyboardButton(text="👤 Profile")],
        [KeyboardButton(text="👩‍❤️‍👨 Lovers"), KeyboardButton(text="🆕 New")]  # New button added
    ],
    resize_keyboard=True
)
disconnect = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Disconnect", callback_data='disconnect')]])
     
                           
rate = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Like", callback_data='like'),InlineKeyboardButton(text="Dislike", callback_data='dislike')]])

more = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Channel", url='https://t.me/LUFZone'),InlineKeyboardButton(text="Chat", url='https://t.me/+Jo7LxVWFlN1kZTBk')],
    [InlineKeyboardButton(text="Support", url='https://t.me/makeitjuicy')]])

more2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Channel", url='https://t.me/LUFZone'),InlineKeyboardButton(text="Chat", url='https://t.me/+Jo7LxVWFlN1kZTBk')]])


support = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Support", url='https://t.me/makeitjuicy')]])
 
mf = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Male"),KeyboardButton(text="Female")]])

mf1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="male1")], [InlineKeyboardButton(text="Female", callback_data="female1")]
    ])
mf2 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Male", callback_data="male2")], [InlineKeyboardButton(text="Female", callback_data="female2")]
    ])

edit = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Edit Name", callback_data="edit_name")], [InlineKeyboardButton(text="Edit Gender", callback_data="edit_gender")], [InlineKeyboardButton(text="Edit Looking For", callback_data="looking_for")]])

balance_bot = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Wallet Bot", url='https://t.me/LUFWalletBot')]])


LINK = "https://vk.com"


# Keyboard setup
launch_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Link", url=LINK)]
    ]
)

ref = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Enter Referral Code", callback_data="enter_referral_code")]
    ])