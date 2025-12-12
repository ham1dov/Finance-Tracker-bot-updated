import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
CREATE_TABLES_PATH = 'create_tables.sql'
DEFAULT_LANGUAGE = os.getenv('DEFAULT_SYSTEM_LANGUAGE')
