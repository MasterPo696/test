from config import router, bot, database, CHANNEL_ID, TOKEN, ProfileCreation
from aiogram.types import Message, ChatMember
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
import app.keyboards.keyboards as kb

# @router.message(ProfileCreation.name)
# async def enter_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await state.set_state(ProfileCreation.gender)
#     await message.answer('Press the button to choose', reply_markup=kb.mf)

# @router.message(ProfileCreation.gender)
# async def enter_gender(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     gender = message.text

#     referal_id = 5228713755

#     data = await state.get_data()
#     database.create_profile(user_id, data["name"], gender, referal_id)
    
#     # Ensure a level entry is created for the user
#     router.cursor.execute("INSERT INTO exp (user_id, level, points) VALUES (?, ?, ?)", (user_id, 0, 0))
#     router.connection.commit()

#     await message.answer(f"Profile created! Your name is {data['name']}.", reply_markup=kb.menu)
#     await state.clear()

