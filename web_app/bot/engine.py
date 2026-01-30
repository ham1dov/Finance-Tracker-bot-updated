import asyncio
import logging
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv

from config import ADMIN_TELEGRAM_ID
from database.db_query import db
from handlers.user_entrypoint import user_router

load_dotenv()

bot = Bot(token=getenv("BOT_TOKEN"))
dp = Dispatcher()
dp.include_router(user_router)

async def start_bot():
    logging.basicConfig(level=logging.INFO)
    await db.connect()
    await db.create_tables()
    try:
        await bot.send_message(ADMIN_TELEGRAM_ID, "Machine is working...")
    except:
        pass
    await dp.start_polling(bot)
