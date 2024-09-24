import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram import Router
from aiogram import F
from config import TOKEN

IMGUR_CLIENT_ID = ""

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик фото
@dp.message(F.photo)
async def get_photo(message: types.Message):

    user_id = message.from_user.id
    # Получаем последнее фото из списка
    photo = message.photo[-1]
    
    # Скачиваем фото с Telegram серверов
    file_info = await bot.get_file(photo.file_id)
    file = await bot.download_file(file_info.file_path)

    # Загружаем фото на Imgur (или другой хостинг)
    url = 'https://api.imgur.com/3/upload'
    headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
    response = requests.post(url, headers=headers, files={'image': file})
    
    # Проверяем результат загрузки
    if response.status_code == 200:
        image_link = response.json()['data']['link']
        await message.answer(f'Фото загружено: {image_link}')
    else:
        await message.answer('Ошибка загрузки фото.')

# Вызов фото по команде
@dp.message(Command('get_photo'))
async def send_photo(message: types.Message):
    # В реальном случае, сохраните ссылку на фото в базе данных
    photo_url = 'https://your-image-host.com/path/to/image.jpg'
    await message.answer_photo(photo=photo_url, caption='Загруженное фото')

