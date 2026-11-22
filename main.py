
from aiogram import Bot, Dispatcher 
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile
from aiogram.enums.dice_emoji import DiceEmoji
from config import BOT_TOKEN,ADMIN_ID
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import asyncio
from  handlers.user.menu import router
from database.models import init_db
from admin_handlers.handlers import router_admin
from middleware.outer_middleware import ThroattingBaseMiddle



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

antispam = ThroattingBaseMiddle(limit_seconds=1.0)






async def main():
    init_db()
    dp.include_router(router)
    dp.include_router(router_admin)
    dp.message.outer_middleware(antispam)
    dp.callback_query.outer_middleware(antispam)
    await dp.start_polling(bot)
    


asyncio.run(main())