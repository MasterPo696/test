import re
import requests
from datetime import datetime
import random
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram import Dispatcher as dp
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TOKEN, ProfileCreation, ETH_WALLET, sticker_pack
import app.keyboards.keyboards as kb
from aiogram import Bot, Dispatcher, types, F


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from app.profile.exp import user_level
from app.chats.call_friends import inline_friends_keyboard
from app.profile.channel import check_user_in_channel
from db.database import Database as db
from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder  

SENDER_WALLET = "TF5rkhN95WQFzvQBmNXqgCTviqVARycMZE"
MY_WALLET = "TRykwnn2CxnnUTQbXc5Git6iJxfxoX596i"
api_key = 'c947ac43-88ea-49ff-877a-e13c83369626'

wallet = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Add wallet", callback_data='add_wallet')], [InlineKeyboardButton(text="Stop", callback_data='stop')]])
yes_no = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Yes", callback_data='yes'), InlineKeyboardButton(text="No", callback_data='no')]])
verification = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Verif", callback_data='verif_wallet'), InlineKeyboardButton(text="Stop", callback_data='stop')]])
send = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Done!", callback_data='done'), InlineKeyboardButton(text="Cancel", callback_data='stop')]])
# change = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Disconect", callback_data='dscnct'), InlineKeyboardButton(text="Cancel", callback_data='stop')]])

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class WalletAdding(StatesGroup):
    wallet = State()
    verifed = State()
    random_number = State()
    used = State()

def is_trc20_address(address: str) -> bool:
    # Регулярное выражение для проверки формата TRC20
    pattern = r"^T[1-9A-HJ-NP-Za-km-z]{33}$"
    
    # Проверка соответствия регулярному выражению
    lol = bool(re.match(pattern, address))
    print(lol)
    return lol


def format_timestamp(timestamp):
    # Преобразование временной метки в читаемый формат
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')


def get_last_20_transactions(tron_address, api_key):
    endpoint = f'https://apilist.tronscan.org/api/transaction?address={tron_address}&limit=20&sort=-timestamp'
    headers = {
        'TRON-PRO-API-KEY': api_key
    }

    data_list = list
    i = 0

    try:
        # Выполняем запрос к API TronScan для получения транзакций
        response = requests.get(endpoint, headers=headers)
        response.encoding = 'utf-8'

        # Проверяем статус ответа
        if response.status_code == 200:
            # Парсим JSON-ответ
            data = response.json()
            data_list =[]
            # Обработка данных о транзакциях
            if data.get('total') > 0 and data.get('data'):
                for tx in data['data']:
                    transaction_hash = tx.get('hash', 'Не указано')
                    sender = tx.get('ownerAddress', 'Не указано')
                    recipient = tx.get('toAddress', 'Не указано')
                    confirmed = tx.get('confirmed', 'Не указано')
                    print 
                    # Преобразуем amount в число, если это строка
                    amount = float(tx.get('amount', '0')) / 1e6
                    timestamp = format_timestamp(tx.get('timestamp', 0))
                    formatted_amount = "{:.6f}".format(amount) 
                    data_list.append([
                        transaction_hash,
                        sender,
                        recipient,
                        confirmed,
                        formatted_amount,
                        timestamp
                    ])
                    
                return data_list
                
            else:
                print("Транзакций не найдено.")
        else:
            print(f"Ошибка запроса. Код ответа: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")







@router.message(Command("balance"))
async def check_user_wallet(message: Message):
    user_id = message.from_user.id
    print(user_id)
    result = db.cursor.execute("SELECT wallet_address, verif FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
    if result:
        address = result[0]
        verif = result[1]
        print(f"this is address: {address}") 
        print(f"this is verif: {verif}") 
        if (verif == 0 or verif == None) or (address == None or address == 0): 
            
            if (address == None or address == "0"):
                await message.answer(f"You don't have the wallet address binded to your account", reply_markup=wallet)
            else:
                await message.answer(f"You haven't verif your wallet address", reply_markup=verification)
        elif verif == 1:
            await message.answer(f"You alredy have an account starting with. {SENDER_WALLET[:5]}")
            await message.answer(f"Do you want to get some more tokens on the balance?")

    else:
        await message.answer("Oops")
    





@router.callback_query(F.data == 'done')
async def sending_callback(call_back: CallbackQuery, state: FSMContext):
    user_id = call_back.from_user.id
    wallet_ok, amount_ok = False, False

    # Получаем последние 20 транзакций для нашего кошелька
    last_transactions_list = get_last_20_transactions(MY_WALLET, api_key)
    # Получаем адрес кошелька пользователя и случайное значение суммы из базы данных
    wallet = db.cursor.execute("SELECT wallet_address, random_int FROM wallets WHERE user_id = ?", (user_id,)).fetchone()

    if wallet:
        wallet_address = wallet[0]
        required_amount = wallet[1]
        print(wallet_address, required_amount)

        # Проходим по каждой транзакции
        for transaction in last_transactions_list:
            tx_wallet = transaction[1]  # Адрес отправителя
            tx_amount = float(transaction[4])  # Сумма транзакции

            # Проверяем, совпадает ли адрес отправителя с кошельком пользователя
            if wallet_address == tx_wallet:
                wallet_ok = True

                # Проверяем, совпадает ли отправленная сумма с требуемой
                if abs(tx_amount - float(required_amount)) < 0.0001:  # Допускаем незначительное отклонение для точности плавающей запятой
                    amount_ok = True
                    break

    # Отправляем сообщение пользователю о результате проверки
    if wallet_ok and amount_ok:
        await call_back.message.answer("Ваш кошелёк и сумма успешно подтверждены!")
        db.cursor.execute("UPDATE wallets SET  verif = ? WHERE user_id = ?", (1, user_id))
    else:
        await call_back.message.answer("Проверка не прошла. Убедитесь, что отправили нужную сумму на правильный кошелёк.")




@router.callback_query(F.data == 'verif_wallet')
async def verif_wallet_callback(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    # wallet = get_wallet(user1_id)
    await state.set_state(WalletAdding.verifed)
    rnd_int = db.cursor.execute("SELECT random_int FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
    if rnd_int:
        await call_back.message.answer(f"Send the <b>{rnd_int[0]} TRX in TRC20 net</b> to", parse_mode="HTML")
        await call_back.message.answer(f"<b>{MY_WALLET}</b> ", parse_mode="HTML")
        await call_back.message.answer(f"<b>Double check the data before sending.</b>", parse_mode="HTML", reply_markup=send)





@router.callback_query(F.data == 'add_wallet')
async def add_wallet_callback(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    # wallet = get_wallet(user1_id)
    await call_back.message.answer("Write down your TRC20 wallet, be sure that's it or u can waste your deposit.")
    await state.set_state(WalletAdding.wallet)






@router.callback_query(F.data == 'stop')
async def stop_callback(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    # wallet = get_wallet(user1_id)
    await call_back.message.answer("You pressed stop.")
    await state.clear()
    return




@router.message(WalletAdding.wallet)
async def add_wallet(message: Message, state: FSMContext):
    wallet_address = str(message.text)
    
    if is_trc20_address(wallet_address):
        await message.answer(f"Your wallet is\n\n{wallet_address}\n\nConfirm?", reply_markup=yes_no)
        await state.update_data(wallet=wallet_address)
    else:
        await message.answer(f"Wrong format, check your wallet and try again.", reply_markup=wallet)  # Use the wallet keyboard





@router.callback_query(F.data == 'yes' or F.data == 'no')
async def yes_or_no_handler(call_back: CallbackQuery, state: StatesGroup):
    user_id = call_back.from_user.id
    data = await state.get_data()
    
    print(data)
    if data:
        address = data['wallet']
        print(address)
        if call_back.data == 'yes':
            # Обновляем данные в таблице
            rnd_int = random.uniform(0.001, 0.3)
            rnd_number = f'{rnd_int:.5f}'
            db.cursor.execute("UPDATE wallets SET wallet_address = ?, random_int = ? WHERE user_id = ?", (address, rnd_number, user_id))
            if address:
                await call_back.message.answer(f"You succesful added {address} to your account.")
        if call_back.data == 'no':
            await call_back.message.answer("You stopped the process.")
            db.cursor.execute("UPDATE wallets SET wallet_address = ?, random_int = ? WHERE user_id = ?", (None, None, user_id))
        db.connection.commit()  # Фиксируем изменения
        await state.clear()





async def main():
    
    logging.info("Routers included. Starting polling...")
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())













# def get_wallet_balance(tron_address, api_key):
#     endpoint = f'https://apilist.tronscan.org/api/account?address={tron_address}'
#     headers = {
#         'TRON-PRO-API-KEY': api_key
#     }

#     try:
#         # Выполняем запрос к API TronScan для получения баланса
#         response = requests.get(endpoint, headers=headers)
#         response.encoding = 'utf-8'

#         # Проверяем статус ответа
#         if response.status_code == 200:
#             # Парсим JSON-ответ
#             data = response.json()
            
#             # Получаем и преобразуем баланс
#             balance = float(data.get('balance', '0'))
#             print(f"Баланс кошелька: {balance} TRX")
#         else:
#             print(f"Ошибка запроса. Код ответа: {response.status_code}")
#     except Exception as e:
#         print(f"Произошла ошибка: {e}")

# # Пример вызова функций

# tron_address = 'TF5rkhN95WQFzvQBmNXqgCTviqVARycMZE'
# api_key = 'c947ac43-88ea-49ff-877a-e13c83369626'

# get_last_20_transactions(tron_address, api_key)
# get_wallet_balance(tron_address, api_key)


# data = get_last_20_transactions(tron_address, api_key)

# print(f"\nHash: {data[0][0]} \nWallet sender: {data[0][1]}\nWallet reciever: {data[0][2]}\nDone? {data[0][3]}\n  Amount = {data[0][4]}TRX")

# print(f"\nHash: {data[1][0]} \nWallet sender: {data[1][1]}\nWallet reciever: {data[1][2]}\nDone? {data[1][3]}\n  Amount = {data[1][4]}TRX")
# # 



# import config
# import logging
# import asyncio
# from aiogram import Bot, Dispatcher
# from config import bot, dp, TOKEN
# # from app.handlers import router
# from app.handlers import router
# from app.frens import fren_router
# from app.forbidden import rep_router
# from app.messages import msg_router
# from balance import usdt_router

