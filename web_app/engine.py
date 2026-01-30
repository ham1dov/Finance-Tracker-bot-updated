import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .stats import router as stats_router  # agar web_app paket bo‘lsa

app = FastAPI(title="Finance Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

app.include_router(stats_router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not os.path.exists(STATIC_DIR):
    print("ERROR: static folder not found at", STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

import asyncio
import logging
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv

from config import ADMIN_TELEGRAM_ID
from database.db_query import db
from handlers.user_entrypoint import user_router

load_dotenv()

# Get the bot token from the environment variables
token = getenv("BOT_TOKEN")

# Initialize the bot and dispatcher
bot = Bot(token=token)
dp = Dispatcher()

# Include the user router
dp.include_router(user_router)


async def main():
    """
    Main function to start the bot.
    """
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    # Connect to the database
    await db.connect()
    await db.create_tables()
    # Start polling for updates
    try:
        await bot.send_message(chat_id=ADMIN_TELEGRAM_ID, text='Machine is working...')
    except:
        pass
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown on keyboard interrupt
        print("Bot stopped")
