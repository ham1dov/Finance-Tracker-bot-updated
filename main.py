import asyncio
import logging
from aiogram import Bot, Dispatcher
from os import getenv
from dotenv import load_dotenv

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
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        # Run the main function
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle graceful shutdown on keyboard interrupt
        print("Bot stopped")
