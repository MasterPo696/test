import re
import requests
import logging
from datetime import datetime
import random
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN, ETH_WALLET
from db.database import Database
import asyncio
import ccxt

# exchange = ccxt.binance()  # Выберите нужную биржу
# ticker = exchange.fetch_ticker('TRX/USDT')  # Замените 'BTC' на нужную вам криптовалюту



# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database()
usdt_router = Router()

# Кнопки и клавиатуры
wallet_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Add wallet", callback_data='add_wallet')],
    [InlineKeyboardButton(text="Stop", callback_data='stop')]
])

verification_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Verify Wallet", callback_data='verify_wallet')],
    [InlineKeyboardButton(text="Stop", callback_data='stop')]
])

choose_currency_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="TRX", callback_data='trx')]
])

confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Done!", callback_data='done')],
    [InlineKeyboardButton(text="Cancel", callback_data='stop')]
])

ok_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="OK", callback_data='ok')]
])

yes_no_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data='yes')],
    [InlineKeyboardButton(text="No", callback_data='no')]
])

get_more = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Get More!", callback_data='get_more')],
    [InlineKeyboardButton(text="It's fine", callback_data='stop')]
])

SENDER_WALLET = "TF5rkhN95WQFzvQBmNXqgCTviqVARycMZE"
MY_WALLET = "TRykwnn2CxnnUTQbXc5Git6iJxfxoX596i"
api_key = 'c947ac43-88ea-49ff-877a-e13c83369626'

# Определение состояний
class WalletStates(StatesGroup):
    wallet = State()
    verified = State()
    amount_usdt = State()

# Проверка TRC20 адреса
def is_trc20_address(address: str) -> bool:
    pattern = r"^T[1-9A-HJ-NP-Za-km-z]{33}$"
    return bool(re.match(pattern, address))

# Форматирование временной метки
def format_timestamp(timestamp):
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

# Получение последних 20 транзакций из TronScan
def get_last_20_transactions(tron_address, api_key):
    endpoint = f'https://apilist.tronscan.org/api/transaction?address={tron_address}&limit=20&sort=-timestamp'
    headers = {'TRON-PRO-API-KEY': api_key}

    try:
        response = requests.get(endpoint, headers=headers)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            data = response.json()
            if data.get('total') > 0 and data.get('data'):
                transactions = []
                for tx in data['data']:
                    amount = float(tx.get('amount', '0')) / 1e6
                    transactions.append({
                        'hash': tx.get('hash', 'Не указано'),
                        'sender': tx.get('ownerAddress', 'Не указано'),
                        'recipient': tx.get('toAddress', 'Не указано'),
                        'confirmed': tx.get('confirmed', 'Не указано'),
                        'amount': "{:.6f}".format(amount),
                        'timestamp': format_timestamp(tx.get('timestamp', 0))
                    })
                return transactions
    except Exception as e:
        logging.error(f"Произошла ошибка при запросе транзакций: {e}")
    return []

# Обработчик команды "Balance"
@usdt_router.message(F.text == "Balance")
async def check_balance(message: Message, state: FSMContext):
    user_id = message.from_user.id
    wallet_data = db.cursor.execute("SELECT wallet_address, verif FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
    balance_count = db.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()

    await message.answer(f"You have {balance_count[0]} on ur balance, do u want to get more?", reply_markup=get_more)
    # Проверка на привязанный кошелек
    if not wallet_data or not wallet_data[0]:
        await message.answer("You don't have a wallet linked. Please add one.", reply_markup=wallet_keyboard)
        return
    
    # Проверка на верификацию кошелька
    if wallet_data[1] == 0 or wallet_data[1] is None:
        await message.answer("Your wallet is not verified. Please verify it.", reply_markup=verification_keyboard)
        return
    
    # Если кошелек верифицирован, предлагаем ввести сумму для пополнения


@usdt_router.callback_query(F.data == 'get_more')
async def add_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter the amount in USDT you want to add to your balance:")
    await state.set_state(WalletStates.amount_usdt)





# Обработчик ввода суммы пополнения
@usdt_router.message(WalletStates.amount_usdt)
async def enter_amount(message: Message, state: FSMContext):
    # trx_price = ticker['last']
    try:
        amount_usdt = float(message.text)
        if amount_usdt <= 0:
            raise ValueError("Amount must be positive.")

        # Сохраняем данные о сумме и времени запроса пополнения
        await state.update_data(amount_usdt=amount_usdt, request_time=datetime.now().timestamp())

        # Предлагаем пользователю отправить TRX
        await message.answer(f"Please send {amount_usdt} TRX to the wallet address:\n\n{MY_WALLET}", reply_markup=confirm_keyboard)
        await state.set_state(WalletStates.verified)
    except ValueError:
        await message.answer("Invalid amount. Please enter a valid number.")

# Обработчик кнопки Done
@usdt_router.callback_query(F.data == 'done')
async def check_transaction(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    wallet_data = db.cursor.execute("SELECT wallet_address FROM wallets WHERE user_id = ?", (user_id,)).fetchone()
    
    if not wallet_data:
        await callback.message.answer("Wallet not found. Please link a wallet first.")
        return

    wallet_address = wallet_data[0]
    user_data = await state.get_data()
    amount_usdt = user_data.get('amount_usdt', 0)
    request_time = user_data.get('request_time', 0)

    # Получаем последние транзакции
    transactions = get_last_20_transactions(MY_WALLET, api_key)

    print(f"Wallet Address: {wallet_address}")
    print(f"Amount USDT: {amount_usdt}")
    print(f"Request Time: {request_time}")
    print(f"Formatted Request Time: {format_timestamp(request_time * 1000)}")
    print("Filtered Transactions:")
    for tx in transactions:
        print(f"Transaction: {tx}")
        print(f"Sender Match: {tx['sender'] == wallet_address}")
        print(f"Amount Match: {abs(float(tx['amount']) - float(amount_usdt)) < 0.0001}")
        print(f"Timestamp Check: {tx['timestamp']} > {format_timestamp(request_time * 1000)}")
        print("---")

    # Фильтрация транзакций, которые произошли после момента запроса
    filtered_transactions = [
        tx for tx in transactions if tx['sender'] == wallet_address and abs(float(tx['amount']) - float(amount_usdt)) < 0.0001 and tx['timestamp'] > format_timestamp(request_time * 1000)
    ]

    for tx in transactions:
        print((float(tx['amount']), float(amount_usdt)))
    

    if filtered_transactions:
        # Успешная проверка, обновляем баланс
        current_balance = db.cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,)).fetchone()[0]
        new_balance = current_balance + amount_usdt
        db.cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        db.connection.commit()

        await callback.message.answer(f"Transaction confirmed! Your new balance is: {new_balance} USDT")
        await state.clear()
    else:
        await callback.message.answer("No matching transaction found. Please check your transaction or try again.")

# Обработчик добавления кошелька
@usdt_router.callback_query(F.data == 'add_wallet')
async def add_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter your TRC20 wallet address.")
    await state.set_state(WalletStates.wallet)



@usdt_router.message(WalletStates.wallet)
async def save_wallet(message: Message, state: FSMContext):
    wallet_address = message.text.strip()
    if is_trc20_address(wallet_address):
        random_amount = random.uniform(0.001, 0.3)
        db.cursor.execute("UPDATE wallets SET wallet_address = ?, random_int = ? WHERE user_id = ?", (wallet_address, random_amount, message.from_user.id))
        db.connection.commit()
        await message.answer(f"Wallet {wallet_address} has been added. Please verify by sending {random_amount:.5f} TRX.", reply_markup=verification_keyboard)
        await state.clear()
    else:
        await message.answer("Invalid wallet format. Please try again.", reply_markup=wallet_keyboard)

# Верификация кошелька
@usdt_router.callback_query(F.data == 'verify_wallet')
async def verify_wallet(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    random_amount = db.cursor.execute("SELECT random_int FROM wallets WHERE user_id = ?", (user_id,)).fetchone()[0]
    await callback.message.answer(f"Please send {random_amount:.3f} TRX to verify your wallet.\n\n{MY_WALLET}", reply_markup=confirm_keyboard)
