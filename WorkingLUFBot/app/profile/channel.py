from aiogram import Bot
from aiogram.types import ChatMember
from aiogram.exceptions import TelegramAPIError
import logging

CHANNEL_ID = '@LUFZone'  # Убедитесь, что CHANNEL_ID соответствует вашему каналу

async def check_user_in_channel(bot: Bot, user_id: int):
    try:
        # Получаем информацию о пользователе в канале
        chat_member: ChatMember = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Проверяем статус пользователя
        if chat_member.status in ['member', 'administrator', 'creator']:
            logging.debug("User is in the channel.")
            return 0
        else:
            logging.warning("User is not in the channel.")
            return 1
    except TelegramAPIError as e:
        logging.error(f"Telegram API error: {e}")
        return 2
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return 2



# For the groups


# @dp.message(F.text ==['text'])
# async def get_chat_id(message: Message):
#     # Print chat ID to the console
#     print("Chat ID:", message.chat.id)

#     # Optionally, reply with the chat ID
#     await message.reply(f"Chat ID: {message.chat.id}")
