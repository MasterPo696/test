import time, pytz
from aiogram import Router, Bot, types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from collections import defaultdict
from random import shuffle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from datetime import datetime, timedelta
from db.database import Database as db
import random 


# Настройки антиспама
MESSAGE_LIMIT = 40  # Лимит сообщений за минуту
TIME_WINDOW = 60  # Время для подсчета количества запросов (в секундах)
COOLDOWN_TIMES = [60, 120, 180, 1000, 10000]  # Время блокировки пользователя (в секундах)

# Храним время последнего сообщения, количество запросов и блокировки для каждого пользователя
user_last_message_time = defaultdict(lambda: datetime(1970, 1, 1, tzinfo=pytz.UTC))
user_requests = defaultdict(list)
user_blocked_until = defaultdict(lambda: datetime(1970, 1, 1, tzinfo=pytz.UTC))  # Время, до которого пользователь заблокирован
user_violations = defaultdict(int)  # Счетчик нарушений пользователя
user_answers = defaultdict(lambda: None)
user_warning_count = defaultdict(int)  # Счетчик предупреждений


# Инициализация бота и роутера
bot = Bot(token=TOKEN)
spam_router = Router()
from aiogram import Router, Bot, types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from collections import defaultdict
from random import shuffle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN
from datetime import datetime, timedelta
import pytz
import random

# Настройки антиспама
MESSAGE_LIMIT = 40  # Лимит сообщений за минуту
TIME_WINDOW = 60  # Время для подсчета количества запросов (в секундах)
WARNING_THRESHOLD = 10  # Порог предупреждений до блокировки
COOLDOWN_TIMES = [60, 120, 180, 1000, 10000]  # Время блокировки пользователя (в секундах)

# Храним время последнего сообщения, количество запросов и блокировки для каждого пользователя
user_last_message_time = defaultdict(lambda: datetime(1970, 1, 1, tzinfo=pytz.UTC))
user_requests = defaultdict(list)
user_blocked_until = defaultdict(lambda: datetime(1970, 1, 1, tzinfo=pytz.UTC))  # Время, до которого пользователь заблокирован
user_violations = defaultdict(int)  # Счетчик нарушений пользователя
user_answers = defaultdict(lambda: None)
user_warning_count = defaultdict(int)  # Счетчик предупреждений

# Инициализация бота и роутера
bot = Bot(token=TOKEN)
spam_router = Router()

class AntiSpamMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data: dict):
        user_id = event.from_user.id
        current_time = datetime.now(pytz.UTC)
        
        # Извлечение метки времени блокировки и конвертация в UTC время
        block_time = user_blocked_until.get(user_id, datetime(1970, 1, 1, tzinfo=pytz.UTC))
        unchained_time = block_time
        
        if current_time < unchained_time:
            # Вычисляем оставшееся время
            time_left = unchained_time - current_time
            days, remainder = divmod(time_left.seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Форматируем время
            time_left_formatted = f"{days} days {hours:02}:{minutes:02}:{seconds:02}"

            await event.answer(f"<b>Damn, you texted too fast, let's cool down :D\n\nYou will be unblocked in {time_left_formatted}</b>", parse_mode="HTML")
            return

        # Проверка частоты сообщений
        last_message_time = user_last_message_time.get(user_id, datetime(1970, 1, 1, tzinfo=pytz.UTC))
        if current_time - last_message_time < timedelta(seconds=1):
            # Увеличиваем счётчик предупреждений
            user_warning_count[user_id] += 1

            if user_warning_count[user_id] >= WARNING_THRESHOLD:
                # Увеличиваем счетчик нарушений
                user_violations[user_id] += 1

                # Выбираем время блокировки на основе количества нарушений
                violation_count = user_violations[user_id]
                cooldown_time = COOLDOWN_TIMES[min(violation_count - 1, len(COOLDOWN_TIMES) - 1)]

                # Блокируем пользователя на это время
                user_blocked_until[user_id] = current_time + timedelta(seconds=cooldown_time)

                # Генерация вопроса и вариантов ответа
                frst_number = random.randrange(0, 9)
                scnd_number = random.randrange(0, 9)
                sights = ["+", "-"]
                sight_random = sights[random.randrange(0, 1)]

                question = str(frst_number) + str(sight_random) + str(scnd_number)

                if sight_random == "+":
                    correct_answer = frst_number + scnd_number
                else: 
                    correct_answer = frst_number - scnd_number

                wrong_1 = correct_answer + 2
                wrong_2 = correct_answer + 1
                wrong_3 = correct_answer - 1
                wrong_answers = [wrong_1, wrong_2, wrong_3]  # Неправильные ответы
                options = [correct_answer] + wrong_answers
                shuffle(options)

                # Сохраняем правильный ответ
                user_answers[user_id] = correct_answer

                # Создаем инлайн-клавиатуру с вариантами ответов
                buttons = [InlineKeyboardButton(text=str(option), callback_data=f"answer:{option}") for option in options]
                keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

                await event.answer(f"<b>You have one of the fastest hands here. Are you not a bot? Answer this: {question}</b>", reply_markup=keyboard, parse_mode="HTML")
                return
            else:
                await event.answer("<b>🚫 Please, don't spam.</b>", parse_mode="HTML")
                return

        # Сбрасываем счётчик предупреждений при нормальном сообщении
        user_warning_count[user_id] = 0

        # Обновляем время последнего сообщения
        user_last_message_time[user_id] = current_time

        # Проверка количества запросов за минуту
        user_requests[user_id].append(current_time)
        user_requests[user_id] = [t for t in user_requests[user_id] if current_time - t < timedelta(seconds=TIME_WINDOW)]

        if len(user_requests[user_id]) > MESSAGE_LIMIT:
            # Увеличиваем счётчик нарушений
            user_violations[user_id] += 1

            # Выбираем время блокировки на основе количества нарушений
            violation_count = user_violations[user_id]
            cooldown_time = COOLDOWN_TIMES[min(violation_count - 1, len(COOLDOWN_TIMES) - 1)]

            # Блокируем пользователя на это время
            user_blocked_until[user_id] = current_time + timedelta(seconds=cooldown_time)

            # Генерация вопроса и вариантов ответа
            frst_number = random.randrange(0, 9)
            scnd_number = random.randrange(0, 9)
            sights = ["+", "-"]
            sight_random = sights[random.randrange(0, 1)]

            question = str(frst_number) + str(sight_random) + str(scnd_number)

            if sight_random == "+":
                correct_answer = frst_number + scnd_number
            else: 
                correct_answer = frst_number - scnd_number

            wrong_1 = correct_answer + 2
            wrong_2 = correct_answer + 1
            wrong_3 = correct_answer - 1
            wrong_answers = [wrong_1, wrong_2, wrong_3]  # Неправильные ответы
            options = [correct_answer] + wrong_answers
            shuffle(options)

            # Сохраняем правильный ответ
            user_answers[user_id] = correct_answer

            # Создаем инлайн-клавиатуру с вариантами ответов
            buttons = [InlineKeyboardButton(text=str(option), callback_data=f"answer:{option}") for option in options]
            keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

            await event.answer(f"<b>You have one of the fastest hands here. Are you not a bot? Answer this: {question}</b>", reply_markup=keyboard, parse_mode="HTML")
            return

        # Передаем данные дальше по цепочке
        return await handler(event, data)



# Обработчик нажатий на кнопки
@spam_router.callback_query(lambda c: c.data and c.data.startswith('answer:'))
async def handle_answer(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_answer = int(callback_query.data.split(':')[1])
    correct_answer = user_answers.get(user_id)

    if selected_answer == correct_answer:
        await bot.send_message(user_id, "<b>Damn, it was good! Your hand is really fast!</b>", parse_mode="HTML")
        user_requests[user_id] = []  # Сбрасываем счетчик запросов
        user_violations[user_id] = 0  # Сбрасываем счетчик нарушений
    else:
        await callback_query.message.reply("<b>Damn... You are the bot as me... Brother?</b>", parse_mode="HTML")
    
    # Убираем кнопки после выбора ответа
    await callback_query.message.edit_reply_markup(reply_markup=None)
