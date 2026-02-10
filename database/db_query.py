from typing import Literal, Union

import asyncpg
from utils.custom_functions import get_current_time
from config import DATABASE_URL_TG, CREATE_TABLES_PATH
class Database:
    def __init__(self):
        self.url = DATABASE_URL_TG
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.url)

    async def get_all_users(self):
        try:
            async with self.pool.acquire() as conn:
                query = """SELECT * FROM users"""
                users = await conn.fetch(query)
                return users
        except Exception as er:
            print('DATABASE ERROR: Error with fetching all users ---', str(er))

    async def create_tables(self):
        try:
            async with self.pool.acquire() as conn:
                with open(CREATE_TABLES_PATH, 'r', encoding='utf-8') as f:
                    sql_query = f.read()

                await conn.execute(sql_query)
        except Exception as er:
            print('DATABASE ERROR: Error with CREATING TABLES --- ', str(er))
            pass

    async def add_income(self, user_id:int, amount:Union[float, int], source:str, payment_method:str='cash', additional_info:str=None, currency:str=None):
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO user_earnings(user_id, amount, currency, source, payment_method, additional_info, inserted_at)
                VALUES($1, $2, $3, $4, $5, $6, $7) RETURNING id
                """
                if currency:
                    return await conn.fetchval(query, user_id, amount, currency, source, payment_method, additional_info, get_current_time())
                else:
                    user_currency = await conn.fetchval("SELECT currency FROM users WHERE telegram_id = $1", user_id)
                    return await conn.fetchval(query, user_id, amount, user_currency, source, payment_method, additional_info, get_current_time())

        except Exception as er:
            print('DATABASE ERROR: Error with INSERTING DATA to user_earnings --- ', str(er))
            return None

    async def add_expense(self, user_id:int, amount:float, source:str, payment_method:str='cash', additional_info:str=None, currency:str=None):
        try:
            async with self.pool.acquire() as conn:
                query = """
                INSERT INTO user_expenses(user_id, amount, currency, source, payment_method, additional_info, inserted_at)
                VALUES($1, $2, $3, $4, $5, $6, $7) RETURNING id
                """
                if currency:
                    return await conn.fetchval(query, user_id, amount, currency, source, payment_method, additional_info, get_current_time())
                else:
                    user_currency = await conn.fetchval("SELECT currency FROM users WHERE telegram_id = $1", user_id)
                    return await conn.fetchval(query, user_id, amount, user_currency, source, payment_method, additional_info, get_current_time())
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
            return language
        except Exception as er:
            print(f'DATABASE ERROR: Error with fetching user[{user_id}] language', str(er))
            return None

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

    async def set_income_additional_info(self, income_id: int, additional_info: str):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as connection:
                query = "UPDATE user_earnings SET additional_info = $1 WHERE id = $2"
                await connection.execute(query, additional_info, income_id)
                print(f'DATABASE SUCCESS: Additional info is set to income[{income_id}]')
        except Exception as er:
            print(f'DATABASE ERROR: Error with setting additional info to income[{income_id}] --- ', str(er))

    async def set_expense_additional_info(self, expense_id: int, additional_info: str):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as connection:
                query = "UPDATE user_expenses SET additional_info = $1 WHERE id = $2"
                await connection.execute(query, additional_info, expense_id)
                print(f'DATABASE SUCCESS: Additional info is set to expense[{expense_id}]')
        except Exception as er:
            print(f'DATABASE ERROR: Error with setting additional info to expense[{expense_id}] --- ', str(er))

    """<---------- Fetching all users incomes ---------->"""

    async def get_all_users_earnings(self):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM user_earnings WHERE TRUE"
                all_incomes = await conn.fetch(query)
                return all_incomes
        except Exception as er:
            print('DATABASE ERROR: Error with fetching all users incomes --- ', str(er))

    """<----------- Fetching all users expenses ----------->"""
    async def get_all_users_expenses(self):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                query = "SELECT * FROM user_expenses WHERE TRUE"
                all_expenses = await conn.fetch(query)
                return all_expenses
        except Exception as er:
            print('DATABASE ERROR: Error with fetching all users expenses --- ', str(er))

    async def delete_transaction(self, table: Literal['user_earnings', 'user_expenses'], transaction_id: int, user_id: int):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                query = f"DELETE FROM {table} WHERE id = $1 AND user_id = $2"
                await conn.execute(query, transaction_id, user_id)
                return True
        except Exception as er:
            print(f'DATABASE ERROR: Error with deleting from {table} --- ', str(er))
            return False

    async def get_categories(self, user_id: int, type: str):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                query = "SELECT name, emoji FROM custom_categories WHERE user_id = $1 AND type = $2"
                rows = await conn.fetch(query, user_id, type)
                if not rows:
                    # Initialize defaults
                    defaults = [
                        ('income', 'salary', '💼'), ('income', 'business', '🏢'), ('income', 'gift', '🎁'),
                        ('expense', 'food', '🍔'), ('expense', 'transport', '🚌'), ('expense', 'shopping', '🛍')
                    ]
                    for t, n, e in defaults:
                        await conn.execute(
                            "INSERT INTO custom_categories(user_id, type, name, emoji) VALUES($1, $2, $3, $4) ON CONFLICT DO NOTHING",
                            user_id, t, n, e
                        )
                    rows = await conn.fetch(query, user_id, type)
                return rows
        except Exception as er:
            print(f'DATABASE ERROR: Error with getting categories --- ', str(er))
            return []

    async def update_transaction(self, table: Literal['user_earnings', 'user_expenses'], transaction_id: int, user_id: int, amount: float, source: str, payment_method: str, additional_info: str = None):
        try:
            if self.pool is None:
                self.pool = await asyncpg.create_pool(self.url)
            async with self.pool.acquire() as conn:
                query = f"""
                UPDATE {table}
                SET amount = $1, source = $2, payment_method = $3, additional_info = $4
                WHERE id = $5 AND user_id = $6
                """
                await conn.execute(query, amount, source, payment_method, additional_info, transaction_id, user_id)
                return True
        except Exception as er:
            print(f'DATABASE ERROR: Error with updating {table} --- ', str(er))
            return False


db = Database()
