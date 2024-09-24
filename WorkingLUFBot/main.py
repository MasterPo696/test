import logging
import asyncio
from aiogram import Bot, Dispatcher
from config import bot, dp, TOKEN
# from app.handlers import router
from app.profile.referrals import ref_router
from app.handlers.commands import router
from app.handlers.menu_buttons import btn_router
from app.chats.call_friends import call_router
from brain.forbidden import  rep_router
from app.chats.messages import msg_router
from app.balance.crypto_balance.get_usdt20 import usdt_router
from app.profile.edit_profile import profile_router
from brain.antispam_mw import AntiSpamMiddleware, spam_router
# from brain.prf_complete_mw import ProfileCompletionMiddleware, complete_profile_router
from quiz_router import quiz_router

from aiogram.fsm.storage.memory import MemoryStorage


dp = Dispatcher(storage=MemoryStorage())
async def main():

    dp.message.middleware(AntiSpamMiddleware())
    # dp.message.middleware(ProfileCompletionMiddleware())
    
    # dp.include_router(quiz_router)
    dp.include_router(spam_router)
    dp.include_router(call_router)
    dp.include_router(router)
    dp.include_router(btn_router)
    dp.include_router(msg_router)
    
    
    # dp.include_router(ref_router)
    # dp.include_router(profile_router)
    # dp.include_router(complete_profile_router)
    # dp.include_router(usdt_router)
    # dp.include_router(rep_router)
    
    logging.info("Routers included. Starting polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

