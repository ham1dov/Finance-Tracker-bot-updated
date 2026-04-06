import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_TELEGRAM_ID = 7583610226
DATABASE_URL_TG = os.getenv('DATABASE_URL_TG')
DATABASE_URL_WEB = os.getenv('DATABASE_URL_WEB')
CREATE_TABLES_PATH = 'database/create_tables.sql'
DEFAULT_LANGUAGE = os.getenv('DEFAULT_SYSTEM_LANGUAGE')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'https://finance-tracker-bot-updated.onrender.com')
