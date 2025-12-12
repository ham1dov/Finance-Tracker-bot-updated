from typing import Literal, Union

import asyncpg
from utils.custom_functions import get_current_time
from config import DATABASE_URL, CREATE_TABLES_PATH
class Database:
    def __init__(self):
        self.url = DATABASE_URL
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)

    async def create_tables(self):
        try:
            async with self.pool.acquire() as conn:
                with open(CREATE_TABLES_PATH, 'r', encoding='utf-8') as f:
                    sql_query = f.read()

                await conn.execute(sql_query)
        except Exception as er:
            print('DATABASE ERROR: Error with CREATING TABLES --- ', str(er))
            pass

    async def add_income(self, user_id:int, amount:Union[float, int], source:str, additional_info:str=None, currency:str=None):
        try:
            async with self.pool.acquire() as conn:
                if currency:
                    query = """
                    INSERT INTO user_earnings(user_id, amount, source, additional_info, inserted_at)
                    VALUES($1, $2, $3, $4, $5, $6) RETURNING id
                    """
                    return await conn.fetchval(query, user_id, amount, currency, source, additional_info, get_current_time())
                else:
                    query = """
                    INSERT INTO user_earnings(user_id, amount, source, currency, additional_info, inserted_at)
                    VALUES($1, $2, $3, $4, $5, $6) RETURNING id
                    """
                    user_currency = await conn.fetchval("SELECT currency FROM users WHERE telegram_id = $1", user_id)
                    return await conn.fetchval(query, user_id, amount, user_currency, source, additional_info, get_current_time())

        except Exception as er:
            print('DATABASE ERROR: Error with INSERTING DATA to user_earnings --- ', str(er))
            return None

    async def add_expense(self, user_id:int, amount:float, source:str, additional_info:str=None, currency:str=None):
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO user_expenses(user_id, amount, currency, source, additional_info, inserted_at)
                VALUES($1, $2, $3, $4, $5, $6) RETURNING id
                """
                if currency:
                    return await conn.execute(query, user_id, amount, currency, source, additional_info, get_current_time())
                else:
                    user_currency = await conn.fetchval("SELECT currency FROM users WHERE telegram_id = $1", user_id)
                    return await conn.execute(query, user_id, amount, user_currency, source, additional_info, get_current_time())
        except Exception as er:
            print('DATABASE ERROR: Error with INSERTING DATA to user_expenses --- ', str(er))
            return None

    async def get_user(self, telegram_id:int):
        try:
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM users WHERE telegram_id = $1"
                user = await conn.fetchrow(query, telegram_id)
                return user
        except Exception as er:
            print('DATABASE ERROR: Error with fetching user info --- ', str(er))
            return None

    async def add_new_user(self, user_id:int, fullname:str,
                           sex:Literal['male', 'female'],
                           status:str,
                           language:Literal['uz', 'en', 'ru'],
                           currency:Literal['uzs', 'eur', 'usd', 'rub']):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)

            async with self.pool.acquire() as conn:
                query = """INSERT INTO users(telegram_id, fullname, sex, social_status, language, currency)
                VALUES($1, $2, $3, $4, $5, $6)
                ON CONFLICT (telegram_id) DO NOTHING;"""
                async with self.pool.acquire() as conn:
                    await conn.execute(query, user_id, fullname, sex, status, language, currency)
        except Exception as er:
            print('DATABASE ERROR: Error with inserting new user to user table', str(er))

    async def delete_user(self, user_id:int):
        try:
            query = """DELETE FROM users WHERE telegram_id = $1"""
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                await conn.execute(query, user_id)
            print(f"DATABASE SUCCESS: Deleting user [user_id = {user_id}] from table 'users' successfully")
        except Exception as er:
            print(f'DATABASE ERROR: Error with deleting user[user_id = {user_id}]', str(er))

    """<---------- Fetching user language ---------->"""
    async def get_user_language(self, user_id:int):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            query = "SELECT language FROM users WHERE telegram_id = $1"
            async with self.pool.acquire() as conn:
                language =  await conn.fetchval(query, user_id)
            print(f"DATABASE SUCCESS: Fetching user[{user_id}] language successfully")
        except Exception as er:
            print(f'DATABASE ERROR: Error with fetching user[{language}] language', str(er))

    async def execute(self, query: str, *args, fetch: bool = False, fetchval: bool = False, fetchrow: bool = False, execute: bool = False, executemany:bool = False):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.url)
            # raise RuntimeError("Database pool is not initialized. Call connect() first.")
        if sum([fetch, fetchval, fetchrow, execute]) > 1:
            raise ValueError("Only one of fetch, fetchval, fetchrow, or execute can be True")
        try:
            async with self.pool.acquire() as connection:
                if fetch:
                    return await connection.fetch(query, *args)
                elif fetchval:
                    return await connection.fetchval(query, *args)
                elif fetchrow:
                    return await connection.fetchrow(query, *args)
                elif execute:
                    return await connection.execute(query, *args)
                elif executemany:
                    return await connection.executemany(query, *args)
                else:
                    raise ValueError("One of fetch, fetchval, fetchrow, or execute must be specified")
        except asyncpg.exceptions.PostgresError as e:
            raise RuntimeError(f"Database query failed: {str(e)}")

    async def set_income_additional_info(self, income_id:str, additional_info:str):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as connection:
                query = "UPDATE user_incomes SET additional_info = $1 WHERE id = $2"
                await connection.execute(query, additional_info, income_id)
                print(f'DATABASE SUCCESS: Additional info is set to income[{income_id}]')
        except Exception as er:
            print(f'DATABASE ERROR: Error with setting additional info to income[{income_id}]')



db = Database()




